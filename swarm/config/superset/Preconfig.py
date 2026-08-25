
# Optional file (which will have to be included on
# the PYTHONPATH) in order to allow to set some variables that will be 
# necessary for the rest of the configuration , e.g. REDIS_BASE_URL that 
# is not set, when running non-dockerized deployment
# This file is loaded at the beginning of superset_georchestra_config.py

import os

REDIS_BASE_URL=f'redis://{os.getenv("REDIS_HOST", "superset_redis")}:{os.getenv("REDIS_PORT", 6379)}'
SQLALCHEMY_DATABASE_URI=f'postgresql://{os.getenv("DATABASE_USER")}:{os.getenv("DATABASE_PASSWORD")}@{os.getenv("DATABASE_HOST")}/{os.getenv("DATABASE_DB")}?options=-c%20search_path=superset'
