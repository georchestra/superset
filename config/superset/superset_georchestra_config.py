# Superset specific config

## Security
# You can generate a strong key using `openssl rand -base64 42`
# SECRET_KEY = 'LwAsS+GcbFUbP52NXNwOsG7u3ZJ+LtjGyXlAhhFX7QgwQDD7Zj/IliEe'
# You can also read it from an environment-variables secret
# SECRET_KEY = env('SUPERSET_SECRET_KEY')

################################
# geOrchestra customizations
################################
ROW_LIMIT = 5000
SUPERSET_WEBSERVER_PORT = 8088
APPKEY = 'superset'

# geOrchestra-specific login logic
from flask_appbuilder.const import AUTH_REMOTE_USER
from GeorchestraCustomizations import GeorchestraSecurityManager, app_init
AUTH_TYPE = AUTH_REMOTE_USER
CUSTOM_SECURITY_MANAGER = GeorchestraSecurityManager
APP_INITIALIZER = app_init
# GEORCHESTRA_ORG_AS_ROLE=False
GEORCHESTRA_ROLES_PREFIX = "ROLE_SUPERSET_"
PUBLIC_ROLE_LIKE = "Gamma"
AUTH_USER_REGISTRATION_ROLE = "Public"
LOGOUT_REDIRECT_URL="/logout"
LOGIN_REDIRECT_URL="/login?service="

from LocalizationFr import *  

# Redefine home page (Superset default is /superset/welcome)
# You can either define a path (including the potential prefix)
# or a view name
# HOME_PAGE_PATH="/dash/dashboard/list"
HOME_PAGE_VIEW="DashboardModelView.list"

DOCUMENTATION_URL = "https://docs.georchestra.org/en/superset/"


################################
# Geo2france custom config
################################

EXTRA_CATEGORICAL_COLOR_SCHEMES =   [
    {
        "id": 'Geo2FranceDefault',
        "description": '',
        "label": 'Geo2France Default',
        "isDefault": False,
        "colors":
         ['#2f85cd','#7900c4','#f700a6','#ff5754','#ffb255','#fbf752','#8eec46','#b2d9cb']
    },
    {
        "id": 'Geo2FranceAlternative',
        "description": '',
        "label": 'Geo2France Alternative',
        "isDefault": False,
        "colors":
         ['#dfe4ea','#5892ee','#8bc832','#8899a8','#155fd5','#456218','#061d41']
    },
    {
        "id": 'Geo2FranceFull',
        "description": '',
        "label": 'Geo2FranceFull',
        "isDefault": False,
        "colors":
         ['#2f85cd','#7900c4','#f700a6','#ff5754','#ffb255','#fbf752','#8eec46','#b2d9cb','#005fb2','#2900a7','#c6007c','#ff3001','#ff9000','#fee300','#8bc800','#00b966','#6ca6d8','#836ad2','#e370b9','#ff9881','#ffc781','#fff07e','#c1e372','#6ddcaa','#0f4395','#210083','#9f0064','#cd2601','#cd7300','#cdb600','#709f02','#007c48']
    }
]

EXTRA_SEQUENTIAL_COLOR_SCHEMES =  [
    {
        "id": 'Geo2FranceDivergenteSmall',
        "description": '',
        "isDiverging": True,
        "label": 'Geo2france Divergente Basic',
        "isDefault": False,
        "colors":
         ['#8BC832','#3758F9','#3758F9','#061D41']
    },
    {
        "id": 'Geo2FranceDivergenteAlternative',
        "description": '',
        "isDiverging": True,
        "label": 'Geo2france Divergente Alternative',
        "isDefault": False,
        "colors":
         ['#dfe4ea','#0f4395','#d948a5','#061d41']
    },
    {
        "id": 'Geo2FranceDivergente',
        "description": '',
        "isDiverging": True,
        "label": 'Geo2france Divergente',
        "isDefault": False,
        "colors":
         ['#DFE4EA','#8BC832','#3758F9','#061D41']
    },
]


################################
# Talisman config
################################
TALISMAN_CONFIG = {
    "content_security_policy": {
        "base-uri": ["'self'"],
        "default-src": ["'self'"],
        "img-src": [
            "'self'",
            "blob:",
            "data:",
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
        "script-src": ["'self'", "'strict-dynamic'", "'unsafe-eval'", "https://cdn.jsdelivr.net/"],
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

