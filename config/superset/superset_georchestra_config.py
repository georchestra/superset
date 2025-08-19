# Superset specific config

import logging
from datetime import timedelta
from os import environ

from GeorchestraCustomizations import CustomLoggingConfigurator
from superset.utils.log import StdOutEventLogger

logger = logging.getLogger(__name__)

LOG_LEVEL = environ.get('LOG_LEVEL', 'INFO').upper()
# Override LOGGING_CONFIGURATOR from
# https://github.com/apache/superset/blob/master/superset/config.py#L933
LOGGING_CONFIGURATOR = CustomLoggingConfigurator()

# Optionally import Preconfig.py (which will have been included on
# the PYTHONPATH) in order to allow to set some variables that will be
# necessary here , e.g. REDIS_BASE_URL that is not set, when running
# non-dockerized deployment
#
try:
    import Preconfig
    from Preconfig import *

    logger.info(
        f"Loaded your preconfig parameters from " f"[{Preconfig.__file__}]"
    )
except ImportError:
    # No preconfig
    pass

## Security
# You can generate a strong key using `openssl rand -base64 42`
# SECRET_KEY = 'LwAsS+GcbFUbP52NXNwOsG7u3ZJ+LtjGyXlAhhFX7QgwQDD7Zj/IliEe'
# You can also read it from an environment-variables secret
# SECRET_KEY = env('SUPERSET_SECRET_KEY')

################################
# geOrchestra customizations
################################
# Make sure PROXY fix is enabled (done by default in dockerized environments but not on manual install)
ENABLE_PROXY_FIX = True

ROW_LIMIT = 5000
SUPERSET_WEBSERVER_PORT = 8088
APPKEY = 'superset'

# geOrchestra-specific login logic
from flask_appbuilder.const import AUTH_REMOTE_USER
from GeorchestraCustomizations import GeorchestraSecurityManager, app_init, NullEventLogger

AUTH_TYPE = AUTH_REMOTE_USER
CUSTOM_SECURITY_MANAGER = GeorchestraSecurityManager
APP_INITIALIZER = app_init
GEORCHESTRA_ROLES_PREFIX = "ROLE_SUPERSET_"
# Check if user roles list needs to be updated. Means DB access so we don't want it to happen too often
GEORCHESTRA_ROLES_CHECK_FREQUENCY = 5 #minutes
# Can configure the header from the georchestra default.properties file
# GEORCHESTRA_PROPERTIES_FILE_PATH = "/etc/georchestra/default.properties"
# GEORCHESTRA_NOHEADER = False
# Can also configure the header directly here with the following params
# GEORCHESTRA_HEADER_SCRIPT = "https://cdn.jsdelivr.net/gh/georchestra/header@dist/header.js"
# GEORCHESTRA_HEADER_HEIGHT = 90
# GEORCHESTRA_HEADER_URL = "/header/"
# GEORCHESTRA_HEADER_CONFIG_FILE = "/header-config.json"
# GEORCHESTRA_HEADER_USE_LEGACY_HEADER = "true"
# GEORCHESTRA_HEADER_STYLESHEET = "http://my-domain-name/stylesheet.css"
# GEORCHESTRA_LOGO_URL = "https://www.georchestra.org/public/georchestra-logo.svg"
# Guest_template role is used to bootstrap the Public role
# See https://docs.georchestra.org/superset/en/latest/technical_guides/administration/making_a_dashboard_public/#importing-the-guest_template-role
PUBLIC_ROLE_LIKE = "Guest_template"
AUTH_USER_REGISTRATION_ROLE = "Public"
LOGOUT_REDIRECT_URL = "/logout"
LOGIN_REDIRECT_URL = "/login?service="

# Enable jinja template processing cf https://superset.apache.org/docs/configuration/sql-templating/#jinja-templates
FEATURE_FLAGS = { "ENABLE_TEMPLATE_PROCESSING": True }

# Disable default event logging (stored in DB by default, which can bloat the DB,
# cf https://github.com/apache/superset/discussions/23110).
# Alternatives are StdOutEventLogger or DBEventLogger (default).
if environ.get('LOG_EVENTS_STDOUT', 'false') in ['true', 'yes']:
    logger.debug("EVENT_LOGGER = StdOutEventLogger()")
    EVENT_LOGGER = StdOutEventLogger()
else:
    logger.debug("EVENT_LOGGER = NullEventLogger()")
    EVENT_LOGGER = NullEventLogger()

from LocalizationFr import *

# Redefine home page (Superset default is /superset/welcome)
# You can either define a path (including the potential prefix)
# or a view name
# HOME_PAGE_PATH="/superset/dashboard/list"
HOME_PAGE_VIEW = "DashboardModelView.list"

DOCUMENTATION_URL = "https://docs.georchestra.org/en/superset/"

################################
# Geo2france custom config
################################

EXTRA_CATEGORICAL_COLOR_SCHEMES = [
    {
        "id": 'Geo2FranceDefault',
        "description": '',
        "label": 'Geo2France Default',
        "isDefault": False,
        "colors":
            ['#2f85cd', '#7900c4', '#f700a6', '#ff5754', '#ffb255', '#fbf752',
             '#8eec46', '#b2d9cb']
    },
    {
        "id": 'Geo2FranceAlternative',
        "description": '',
        "label": 'Geo2France Alternative',
        "isDefault": False,
        "colors":
            ['#dfe4ea', '#5892ee', '#8bc832', '#8899a8', '#155fd5', '#456218',
             '#061d41']
    },
    {
        "id": 'Geo2FranceFull',
        "description": '',
        "label": 'Geo2FranceFull',
        "isDefault": False,
        "colors":
            ['#2f85cd', '#7900c4', '#f700a6', '#ff5754', '#ffb255', '#fbf752',
             '#8eec46', '#b2d9cb', '#005fb2', '#2900a7', '#c6007c', '#ff3001',
             '#ff9000', '#fee300', '#8bc800', '#00b966', '#6ca6d8', '#836ad2',
             '#e370b9', '#ff9881', '#ffc781', '#fff07e', '#c1e372', '#6ddcaa',
             '#0f4395', '#210083', '#9f0064', '#cd2601', '#cd7300', '#cdb600',
             '#709f02', '#007c48']
    }
]

EXTRA_SEQUENTIAL_COLOR_SCHEMES = [
    {
        "id": 'Geo2FranceDivergenteSmall',
        "description": '',
        "isDiverging": True,
        "label": 'Geo2france Divergente Basic',
        "isDefault": False,
        "colors":
            ['#8BC832', '#3758F9', '#3758F9', '#061D41']
    },
    {
        "id": 'Geo2FranceDivergenteAlternative',
        "description": '',
        "isDiverging": True,
        "label": 'Geo2france Divergente Alternative',
        "isDefault": False,
        "colors":
            ['#dfe4ea', '#0f4395', '#d948a5', '#061d41']
    },
    {
        "id": 'Geo2FranceDivergente',
        "description": '',
        "isDiverging": True,
        "label": 'Geo2france Divergente',
        "isDefault": False,
        "colors":
            ['#DFE4EA', '#8BC832', '#3758F9', '#061D41']
    },
]

################################
# Web Security config
################################

# You will need this for instance to embed mviewer maps in Superset
HTML_SANITIZATION = True
# Allow iframes
HTML_SANITIZATION_SCHEMA_EXTENSIONS = {
"attributes": {
    "*": ["style","className"],
    "iframe": ["src"]
},
    "tagNames": ["style","iframe"]
}

TALISMAN_CONFIG = {
    "content_security_policy": {
        "base-uri": ["'self'"],
        "default-src": ["'self'"],
        "img-src": [
            "'self'",
            "blob:",
            "data:",
            "https://www.georchestra.org",
            "https://apachesuperset.gateway.scarf.sh",
            "https://static.scarf.sh/",
            # "https://avatars.slack-edge.com", # Uncomment when SLACK_ENABLE_AVATARS is True  # noqa: E501
        ],
        "worker-src": ["'self'", "blob:"],
        "connect-src": [
            "'self'",
            "https://api.mapbox.com",
            "https://events.mapbox.com",
        ],
        "object-src": "'none'",
        "style-src": [
            "'self'",
            "'unsafe-inline'",
        ],
        # unsafe-eval and cdn are necessary for the geOr header webcomponent to work
        "script-src": ["'self'", "'strict-dynamic'", "'unsafe-eval'", "https://cdn.jsdelivr.net/"],

        # Those 2 lines are related to iframe embedding (e.g. to embed an mviewer map from another domain)
        # frame-ancestors = allow to embed this superset's visualizations to be embedded in www.geo2france.fr content
        # frame-src = allow to embed for instance a mviewer map from www.geo2france.fr in this Superset instance (in a dashboard)
        "frame-ancestors" : "www.geo2france.fr",
        "frame-src" : ["'self'", "www.geo2france.fr"],
    },
    "content_security_policy_nonce_in": ["script-src"],
    "force_https": False,
    "session_cookie_secure": False,
}

################################
# Use redis for caching and rate limit
################################

CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': f"{REDIS_BASE_URL}/3",
    'CACHE_DEFAULT_TIMEOUT': 86400,
    'CACHE_KEY_PREFIX': 'SUPERSET_VIEW'
}

DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': f"{REDIS_BASE_URL}/3",
    'CACHE_DEFAULT_TIMEOUT': 86400,
    'CACHE_KEY_PREFIX': 'SUPERSET_DATA'
}

EXPLORE_FORM_DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': f"{REDIS_BASE_URL}/3",
    'CACHE_DEFAULT_TIMEOUT': 86400,
    'CACHE_KEY_PREFIX': 'SUPERSET_E'
}

FILTER_STATE_CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': f"{REDIS_BASE_URL}/3",
    'CACHE_DEFAULT_TIMEOUT': 86400,
    'CACHE_KEY_PREFIX': 'SUPERSET_F'
}

RATELIMIT_STORAGE_URI = f"{REDIS_BASE_URL}/4"
RATELIMIT_STORAGE_OPTIONS = {"socket_connect_timeout": 30}


# Optionally import Overrides.py (which will have been included on
# the PYTHONPATH) in order to allow some final, custom overrides
#
try:
    import Overrides
    from Overrides import *

    logger.info(
        f"Loaded your preconfig parameters from " f"[{Overrides.__file__}]"
    )
except ImportError:
    # No overrides
    pass
