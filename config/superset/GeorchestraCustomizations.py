import logging
import warnings
from configparser import ConfigParser
from datetime import datetime, timedelta
from itertools import chain
from typing import Any

from flask import redirect, request, url_for, config as flask_config
from flask_appbuilder import expose, IndexView
from flask_appbuilder.security.decorators import no_cache
from flask_appbuilder.security.views import AuthRemoteUserView
from flask_login import logout_user, login_user, current_user

from superset import SupersetSecurityManager, appbuilder, security_manager as sm
from superset.app import SupersetAppInitializer
from superset.superset_typing import FlaskResponse
from superset.utils.log import AbstractEventLogger
from superset.utils.logging_configurator import LoggingConfigurator

logger = logging.getLogger(__name__)


class GeorchestraRemoteUserView(AuthRemoteUserView):
    # Handle custom login/logout logic.
    # But actually, most of the custom logic will be found in RemoteUserLogin class
    # since we're not using the Superset `login` action => login() won't be called
    # unless we ask for an unauthorized path. Even then, it might be called too late
    # (e.g. /superset/dashboard is also allowed to anonymous, so login won't be called. '
    # 'It might be for the event logger, but too late for this display. You'll get
    # authenticated for the next page load. A bummer)
    # => We have to implement a before_request() trigger.

    # Leave blank
    login_template = ''

    def __init__(self):
        super().__init__()
        self.LOGIN_REDIRECT_URL = appbuilder.app.config.get("LOGIN_REDIRECT_URL", "")
        self.LOGOUT_REDIRECT_URL = appbuilder.app.config.get("LOGOUT_REDIRECT_URL", "")

    @expose("/logout/")
    def logout(self):
        # In theory never used (logout button from superset is hidden)
        logger.warning(
            "Logged out from GeorchestraRemoteUserView. This is not expected behaviour")
        logout_user()
        return redirect(self.LOGOUT_REDIRECT_URL)

    @expose('/login/', methods=["GET", "POST"])
    @no_cache
    def login(self):
        """
        If LOGIN_REDIRECT_URL is relative, append it to the URL. Should be the 
        current logic with the Gateway (requires GW >= 2.0.1)
        If not, redirect to the LOGIN_REDIRECT_URL
        """
        logger.info("Using custom security manager")
        next_url = request.args.get("next", "")
        if (self.LOGIN_REDIRECT_URL.startswith("?")
            and not next_url.endswith(self.LOGIN_REDIRECT_URL)):
            # Second part is a failsafe to avoid infinite loop if login strategy is not working as expected
            return redirect(next_url + self.LOGIN_REDIRECT_URL)
        return redirect(self.LOGIN_REDIRECT_URL)


def get_username(environ):
    user = environ.get('HTTP_SEC_USERNAME', None)
    environ['REMOTE_USER'] = user
    return user


class GeorchestraSecurityManager(SupersetSecurityManager):
    authremoteuserview = GeorchestraRemoteUserView

    def __init__(self, appbuilder):
        super(GeorchestraSecurityManager, self).__init__(appbuilder)


class RemoteUserLogin(object):
    # found at https://github.com/apache/superset/discussions/27451
    
    # Frequence to check if user roles list needs to be updated, in minutes. Means DB 
    # access so we don't want it to happen too often
    roles_default_check_frequency = 5
    
    # A dict. Stores for each logged-in username the last time the roles were checked
    roles_checks = dict()

    def __init__(self, app):
        self.app = app

        self.ROLES_PREFIX = app.config.get("GEORCHESTRA_ROLES_PREFIX", "ROLE_SUPERSET_")
        self.ROLES_CHECK_FREQUENCY = app.config.get("GEORCHESTRA_ROLES_CHECK_FREQUENCY",
                                                     self.roles_default_check_frequency)
        try:
            self.ROLES_CHECK_FREQUENCY = int(self.ROLES_CHECK_FREQUENCY)
        except ValueError:
            self.ROLES_CHECK_FREQUENCY = self.roles_default_check_frequency
            logger.warning(f"Invalid value for ROLES_CHECK_FREQUENCY: {self.ROLES_CHECK_FREQUENCY}. Using default value: {self.roles_default_check_frequency}")

        self.AUTH_USER_DEFAULT_ROLE = app.config.get("AUTH_USER_REGISTRATION_ROLE",
                                                     "Public")
        # We need the user to have at least a Public role, no role at all is _bad_

    def get_valid_roles_from_header(self, georchestra_roles: str) -> list[str]:
        """
        Split and filter roles based on the list provided in the HTTP headers
        :param georchestra_roles: comma-separated list of geOrchestra roles. superset relevant roles are expected
        to have a ROLE_SUPERSET_ prefix
        :return: a list of superset-relevant roles
        """
        all_superset_roles = sm.get_all_roles()

        roles_list = georchestra_roles.split(";")
        superset_roles = [role.replace(self.ROLES_PREFIX, "", 1).upper() for role in
                          roles_list if role.startswith(self.ROLES_PREFIX)]

        valid_roles = [r for r in all_superset_roles if r.name.upper() in superset_roles]
        if not valid_roles:
            # We need the user to have at least a role. If none, let it be `Public`
            valid_roles = [sm.find_role(self.AUTH_USER_DEFAULT_ROLE)]
        return valid_roles


    def log_user(self, environ) -> tuple[object, bool]:
        """
        Handle the login logic based on the HTTP headers and the currently logged-in
        user profile if there is one.
        Logic is as follows:
        - check if we have a currently logged in user
            - yes ? -> we check if the username in the sec-headers matches the currently
            logged in user.
            We also might do a periodical roles-check. It doesn't make sense to check
            everytime, but once every, says, 5 mins. To cover the case where a user is
            still logged in but his roles list has changed (would not be detected
            automatically). In that case if necessary we update the user with the
            updated roles.
            => we're good, no change, we return the logged in user. It's
            the most common use-case, so we make it the priority and quit the function
            as fast as possible
            - no ?  -> the user changed since last request, log him out continue (new
            user will be logged in later in this function)
        - check if there is a username sec-header
            - no ?  -> it's an anonymous connection
            - yes ? -> then we have a freshly logged-in user.
                Check if user exists in DB:
                - yes ? -> we update the user's roles in case they changed and log him in
                - no ?  -> we create the user, log him in and move on
        Returns a tuple as we are interested in 2 information:
        - the user object
        - whether is was different from an existing session (means the logged-in user
        changed). In that case, we might
        take some measures, like rerouting to the welcome page
        :param environ:
        :return: (user:object, is_different_user:bool) tuple
        """
        is_different_user = False
        headers_username = get_username(environ)

        if current_user and current_user.is_authenticated:
            if current_user.username == headers_username:
                logging.debug(f"Remote user {headers_username} already logged")
                # Check if roles have changed since the session was started
                # Check is done every GEORCHESTRA_ROLES_CHECK_FREQUENCY times only,
                # to avoid calling DB on each call of the log_user function
                # (can happen more than 10 times per page load)
                last_check = self.roles_checks.get(headers_username, datetime.fromtimestamp(0))
                if datetime.now() > last_check + timedelta(minutes=self.ROLES_CHECK_FREQUENCY):
                    self.roles_checks[headers_username] = datetime.now()
                    georchestra_roles = environ.get('HTTP_SEC_ROLES', "")
                    r = self.get_valid_roles_from_header(georchestra_roles)
                    if r != current_user.roles:
                        # Then update roles in user definition
                        current_user.roles = r
                        sm.update_user(current_user)
                        login_user(current_user)
                return current_user, False
            else:
                # The user changed since last request, log him out and switch to new user
                logout_user()
                is_different_user = True

        # Handle anonymous case (not logged-in)
        if not headers_username:
            # Log out eventually logged-in previous user and switch to anonymous
            logout_user()
            return None, True
        else:
            logger.debug(f"Remote user {headers_username} logs in")

        # We're left with the case where the user has just logged in (no current_user)
        # but http sec-headers indicate a logged-in user

        # Retrieve the user from the DB, if he exists
        user = sm.find_user(username=headers_username)
        # Retrieve roles from http header and filter to the ones relevant in Superset context
        georchestra_roles = environ.get('HTTP_SEC_ROLES', "")
        user_roles = self.get_valid_roles_from_header(georchestra_roles)

        # Update the user if he exists, create him if not
        if user:
            logger.debug("New user logged in: %s", user.username)
            if user.roles != user_roles:
                logger.debug("User exists but roles differ. Updating profile")
                # Update relevant profile information
                user.roles = user_roles
                sm.update_user(user)
        else:
            # Create user
            logger.debug("User not found, creating it")
            user = sm.add_user(
                    username=headers_username,
                    first_name=request.headers.environ.get('HTTP_SEC_FIRSTNAME',
                        headers_username),
                    last_name=request.headers.environ.get('HTTP_SEC_LASTNAME', ""),
                    email=request.headers.environ.get('HTTP_SEC_EMAIL', ""),
                    role=user_roles
               )

            user = sm.auth_user_remote_user(headers_username)

        login_user(user)
        return user, is_different_user

    def before_request(self):
        """
        Manage user REMOTE login
        Important things here happen in log_user function
        :return:
        """
        user, is_different_user = self.log_user(request.environ)
        if not user:
            logger.debug("Logged in as anonymous user")


class GeorchestraContextProcessor(object):
    """
    Provide a context_processor that will inject configuration data into the jinja2 templates.
    It will support
    - parsing default.properties geOrchestra configuration file
    - parsing config values from the superset config files
    """

    def __init__(self, app):
        self.sections = None
        self.app = app
        self.properties_file_path = app.config.get("GEORCHESTRA_PROPERTIES_FILE_PATH",
                                                   "")
        self.noheader = app.config.get("GEORCHESTRA_NOHEADER", False)

    def init_app(self) -> None:
        """
        Load the geOrchestra configuration (datadir/default.properties)
        into the Flask app context
        :return:
        """
        if self.app:
            self.app.context_processor(self.get_georchestra_properties)

    def get_georchestra_properties(self):
        """
        Try to parse geOrchestra default.properties file if provided,
        then override any value by uppercase params from the Superset config files
        :return:
        """
        if self.noheader:
            return {"georchestra": {'noheader': True, }}

        self.sections = dict()
        if self.properties_file_path:
            parser = ConfigParser()
            with open(self.properties_file_path) as lines:
                # ConfigParser complains about missing sections in the file. This line
                # does the trick:
                lines = chain(("[section]",), lines)
                parser.read_file(lines)
                self.sections['default'] = parser['section']
        properties = {
            'headerScript': self.get("GEORCHESTRA_HEADER_SCRIPT", 'headerScript'),
            'headerHeight': self.get("GEORCHESTRA_HEADER_HEIGHT", 'headerHeight'),
            'headerUrl': self.get("GEORCHESTRA_HEADER_URL", 'headerUrl'),
            'headerConfigFile': self.get("GEORCHESTRA_HEADER_CONFIG_FILE",
                                         'headerConfigFile'),
            'useLegacyHeader': self.get("GEORCHESTRA_HEADER_LEGACY_HEADER",
                                        'useLegacyHeader'),
            'georchestraStyleSheet': self.get("GEORCHESTRA_HEADER_STYLESHEET",
                                              'georchestraStyleSheet'),
            'logoUrl': self.get("GEORCHESTRA_LOGO_URL", 'logoUrl'),
            'noheader': self.noheader,
        }
        return {"georchestra": properties}

    def get(self, param_key, prop_key, section='default'):
        """
        :param param_key: key allowed in superset config files
        :param prop_key: key allowed in geOrchestra config files
        :param section: 
        :return: 
        """
        if self.app.config.get(param_key):
            return self.app.config.get(param_key)
        elif section in self.sections:
            return self.sections[section].get(prop_key, None)
        else:
            return None


# Redefine home page (Superset default is /superset/welcome)
# You can either define a path (including the potential prefix)
# or a view name

class SupersetIndexView(IndexView):
    @expose("/")
    def index(self) -> FlaskResponse:
        welcome_viewname = self.appbuilder.app.config.get("HOME_PAGE_VIEW",
                                                          "Superset.welcome")
        welcome_path = self.appbuilder.app.config.get("HOME_PAGE_PATH",
                                                      url_for(welcome_viewname))
        return redirect(welcome_path)


def app_init(app):
    # Activate the geOrchestra REMOTE_USER logic
    logger.info("REMOTE_USER Registering RemoteUserLogin")
    app.before_request(RemoteUserLogin(app).before_request)

    # Set the home page
    app.config[
        'FAB_INDEX_VIEW'] = f"{SupersetIndexView.__module__}.{SupersetIndexView.__name__}"

    # Read default.properties file from geOrchestra datadir
    # Used to configure the geOrchestra header (unless superset's config
    # has GEORCHESTRA_NOHEADER=True in that case,
    # no header will be shown)
    GeorchestraContextProcessor(app).init_app()
    return SupersetAppInitializer(app)

# Alternatively, this should also be possible using FLASK_APP_MUTATOR
# see https://superset.apache.org/docs/configuration/configuring-superset/
# or https://stackoverflow.com/questions/51776567/superset-customization-extend-modify


class NullEventLogger(AbstractEventLogger):
    """Event logger that does nothing"""

    def log(  # pylint: disable=too-many-arguments
        self,
        user_id: int | None,
        action: str,
        dashboard_id: int | None,
        duration_ms: int | None,
        slice_id: int | None,
        referrer: str | None,
        curated_payload: dict[str, Any] | None,
        curated_form_data: dict[str, Any] | None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        pass

# TODO: an event logger that will log interesting events to the analytics module


class CustomLoggingConfigurator(LoggingConfigurator):
    def configure_logging(
        self, app_config: flask_config.Config, debug_mode: bool
    ) -> None:
        if app_config["SILENCE_FAB"]:
            logging.getLogger("flask_appbuilder").setLevel(logging.ERROR)

        # Ignore Werkzeug LocalProxy errors. Doesn't seem to work right now)
        # https://github.com/apache/superset/issues/29403#issuecomment-2532848376
        warnings.filterwarnings("ignore", message = ".*werkzeug.local.LocalProxy.*")

        # basicConfig() will set up a default StreamHandler on stderr
        logging.basicConfig(format=app_config["LOG_FORMAT"])
        logging.getLogger().setLevel(app_config["LOG_LEVEL"])

        logger.info("Logging was configured successfully using CustomLoggingConfigurator")
