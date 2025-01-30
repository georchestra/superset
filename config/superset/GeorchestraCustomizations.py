from superset import security_manager as sm
from superset.security import SupersetSecurityManager
from flask import request, redirect, flash, g, session
from flask_appbuilder.security.views import expose, AuthRemoteUserView
from flask_appbuilder.security.decorators import has_access, no_cache
from flask_appbuilder._compat import as_unicode
from flask_login import login_user, logout_user

import logging

logger = logging.getLogger(__name__)


class GeorchestraRemoteUserView(AuthRemoteUserView):
    # Handle custom login/logout logic.
    # But actually, most of the custom logic will be found in RemoteUserLogin class


    # Leave blank
    login_template = ''

    def __init__(self):
        self.LOGIN_REDIRECT_URL = appbuilder.app.config.get("LOGIN_REDIRECT_URL", "")
        self.LOGOUT_REDIRECT_URL = appbuilder.app.config.get("LOGOUT_REDIRECT_URL", "")

    @expose("/logout/")
    def logout(self):
        logout_user()
        return redirect(self.LOGOUT_REDIRECT_URL)

    @expose('/login/', methods=["GET", "POST"])
    @no_cache
    def login(self):
        logger.info("Using custom security manager")
        return redirect(self.LOGIN_REDIRECT_URL)


class GeorchestraSecurityManager(SupersetSecurityManager):
    authremoteuserview = GeorchestraRemoteUserView
    def __init__(self, appbuilder):
        super(GeorchestraSecurityManager, self).__init__(appbuilder)


class RemoteUserLogin(object):
    # found at https://github.com/apache/superset/discussions/27451

    def __init__(self, app):
        self.app = app

        self. ROLES_PREFIX = app.config.get("GEORCHESTRA_ROLES_PREFIX", "ROLE_SUPERSET_")
        self.USE_ORG_AS_ROLE = app.config.get("GEORCHESTRA_ORG_AS_ROLE", False)
        self.AUTH_USER_DEFAULT_ROLE = app.config.get("AUTH_USER_REGISTRATION_ROLE", "Public")

    def get_roles_from_header(self, georchestra_roles: str) -> list[str]:
        """
        Split and filter roles based on the list provided in the HTTP headers
        :param georchestra_roles: comma-separated list of geOrchestra roles. superset relevant roles are expected
        to have a ROLE_SUPERSET_ prefix
        :return: a list of superset-relevant roles
        """
        roles_list = georchestra_roles.split(";");
        superset_roles = [role.replace(self.ROLES_PREFIX, "", 1).upper()
                          for role in roles_list if role.startswith(self.ROLES_PREFIX)]
        return superset_roles

    def log_user(self, environ)-> tuple[object, bool]:
        """
        Handle the login logic based on the HTTP headers and the currently logged-in user profile if there is
        Logic is as follows:
        - we check for a username header
            - no ? -> it's an anonymous connection
            - yes ? -> we check if it matches an eventual existing session
                - yes ? -> we update the user's roles in case they changed and move on
                - no ? -> we close the existing session then we check if the user exists
                    - yes ? -> we update the user's roles in case they changed and move on
                    - no ? -> we create the user, log him in and move on
        Returns a tuple as we are interested in 2 informations:
        - the user object
        - whether is was different from an existing session (means the logged-in user changed). In that case, we might
        take some measures, like rerouting to the welcome page
        :param environ:
        :return: (user:object, is_different_user:bool) tuple
        """
        is_different_user = False

        headers_username = self.get_username(environ)

        # If we have an existing session, we check if it looks still valid
        if hasattr(g, "user") and hasattr(g.user, "username"):
            if g.user.username == headers_username:
                logging.info("REMOTE_USER user already logged")
                # We still want to check if his roles have changed (done below)
                # return g.user
            else:
                logout_user()
                is_different_user = True

        # Handle anonymous case (not logged-in)
        if not headers_username:
            # Log out eventually logged-in previous user and switch to anonymous
            logout_user()
            return None, is_different_user

        # Retrieve the user from the DB, if he exists
        user = sm.find_user(username=headers_username)

        # Retrieve roles from http header dans filter to the ones relevant in Superset context
        georchestra_roles = environ.get('HTTP_SEC_ROLES', "")
        user_roles = self.get_roles_from_header(georchestra_roles)
        valid_roles = [r for r in sm.get_all_roles() if r.name.upper() in user_roles]
        logger.debug(f"Valid roles for current user {headers_username}: {valid_roles}")
        if not valid_roles:
            valid_roles = [sm.find_role(self.AUTH_USER_DEFAULT_ROLE)]
        logger.debug(f"Valid roles for current user: {valid_roles}")

        logger.debug("REMOTE_USER Look up user: %s", user)
        # Update the user if he exists, create him if not
        if user:
            logger.debug("REMOTE_USER Login_user: %s", user)
            logger.debug("User exists. Updating profile")
            # Update relevant profile information
            user.roles = valid_roles
            sm.get_session.commit()
        else:
            # Create user
            logger.debug("User not found, creating it")
            user = sm.add_user(
                username = headers_username,
                first_name = request.headers.environ.get('HTTP_SEC_FIRSTNAME', headers_username),
                last_name = request.headers.environ.get('HTTP_SEC_LASTNAME', ""),
                email = request.headers.environ.get('HTTP_SEC_EMAIL', ""),
                role=valid_roles)

            flash(as_unicode(f"Welcome to Superset, {headers_username}"), 'info')
            user = sm.auth_user_remote_user(headers_username)

        login_user(user)
        return user, is_different_user

    def get_username(self, environ):
        user = environ.get('HTTP_SEC_USERNAME', None)
        environ['REMOTE_USER'] = user
        return user

    def before_request(self):
        """
        Manage user REMOTE login
        Important things here happen in log_user function
        :return:
        """
        user, is_different_user = self.log_user(request.environ)
        if not user:
            logger.debug("Logged in as anonymous user")


# Redefine home page (Superset default is /superset/welcome)
# You can either define a path (including the potential prefix)
# or a view name
from flask import redirect, g, request, url_for
from flask_appbuilder import expose, IndexView
from superset.extensions import appbuilder
from superset.superset_typing import FlaskResponse

class SupersetIndexView(IndexView):
    @expose("/")
    def index(self) -> FlaskResponse:
        welcome_viewname = self.appbuilder.app.config.get("HOME_PAGE_VIEW", "Superset.welcome")
        welcome_path = self.appbuilder.app.config.get("HOME_PAGE_PATH", url_for(welcome_viewname))
        return redirect(welcome_path)


from superset.app import SupersetAppInitializer
def app_init(app):
    logger.info("REMOTE_USER Registering RemoteUserLogin")
    app.before_request(RemoteUserLogin(app).before_request)

    app.config['FAB_INDEX_VIEW'] = f"{SupersetIndexView.__module__}.{SupersetIndexView.__name__}"
    return SupersetAppInitializer(app)

logger.info(f"Using custom REMOTE_USER logic")
# Alternatively, this should also be possible using FLASK_APP_MUTATOR
# see https://superset.apache.org/docs/configuration/configuring-superset/ or https://stackoverflow.com/questions/51776567/superset-customization-extend-modify





