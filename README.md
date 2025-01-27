# A dashboard app in geOrchestra using Apache Superset

## About
The geOrchestra community has chosen Apache Superset to feature a dashboarding capacity.

It is currently using a fork of the [upstream repo](https://github.com/apache/superset), adding the capacity to serve Superset under a path prefix (e.g. https://demo.georchestra.org/dashboards/). This functionality is ported by a PR that is, at the time of writing this doc, not yet merged upstream: https://github.com/apache/superset/pull/30134


## Use the geOrchestra applicative database for Superset config (so-called "Metadata DB")

Superset uses a database to store their applicative configuration, they call it the[ "Metadata database"](https://superset.apache.org/docs/configuration/configuring-superset#setting-up-a-production-metadata-database). One of the main supported DBMS being Postgresql.

geOrchestra already provides a database for all its apps (not the data. The applications DB): each app is having one dedicated schema. It makes sense to tell Superset to use it for their "applicative DB too.

- Create the schema in your geOrchestra DB. Create a dedicated user too, owning this schema. Superset does not manage the selection of the schema, so ou have to set this user's search path to the given schema *only*. Example code:
```
CREATE USER superset WITH ENCRYPTED PASSWORD 'superset';
CREATE SCHEMA AUTHORIZATION superset;
ALTER ROLE superset SET search_path = superset;
```
- Tell Superset to use it. Depending on the deployment method, you will have to configure the SQLAlchemy connection string in the config file, or to set some environment variables. Please follow the instructions below for your chosen deployment method.


## Deploy using Kubernetes helm chart

There are several config files to load:
- **config/superset/superset_georchestra_config.py** is the main entry point, and this is the one you will be most likely to modify. The provided version makes also use of the following:
- **config/superset/LocalizationFr.py** provides some french locale stuff. It's likely you won't have to change it. If you want to provide support for another locale, you can copy it, adapt it and use your version instead/alongside
- **config/superset/GeorchestraCustomizations.py** provides georchestra-specific logic
  - authentication: rely on REMOTE_USER auth (http sec- headers fed by the gateway/SP)
  - redirection to a custom welcome page


The recommended way is to tell helm to load your config files using --set-file options. It would look like the following:
```bash
helm upgrade --install mysuperset superset/superset \
  -f kubernetes/georchestra-values.yaml \
  --set-file extraSecrets."LocalizationFr\.py"=config/superset/LocalizationFr.py \
  --set-file extraSecrets."GeorchestraCustomizations\.py"=config/superset/GeorchestraCustomizations.py \
  --set-file configOverrides.customconfig=config/superset/superset_georchestra_config.py \
  --set configOverrides.secretkey="SECRET_KEY = 'LwAsS+GcbFUbP52NXNwOsG7u3ZJ+LtjGyXlAhhFX7QgwQDD7Zj/IliEe'"
```

Alternatively, you can copy the content of the config/ folder into the kubernetes/georchestra-values.yaml file, there are placeholders showing you where to paste them.

### Changing the path prefix where Superset is accessed

By default, the superset app will be accessed under `/dash` path. This can quite easily be changed:
- In the georchestra-values.yaml, 
  - Change the value of the `SUPERSET_APP_ROOT` env var.
  - Update accordingly the paths for the healthchecks.
  - Restart the web app.
- Update accordingly the configuration for the SP/gateway

### Use the geOrchestra applicative database instead of the one provided with superset
- Follow the instructions from the _Use the geOrchestra applicative database_ section above.
- Tell Superset to use it. Create a secret providing the connection parameters. It will override the default Superset, so you will have to follow its structure. And example is provided in kubernetes/sample-db-secret.yml. You will notice this secret also adds a SUPERSET_SECRET_KEY, securing the management of the app's secret key.
- Adjust the chart's values  accordingly
  - disable the secretEnv creation
  - provide your custom secret replacement
  - this would give the following adjusted helm command:
```bash
helm upgrade --install -n sup mysuperset superset/superset \
  -f kubernetes/georchestra-values.yaml \
  --set-file extraSecrets."LocalizationFr\.py"=config/superset/LocalizationFr.py \
  --set-file extraSecrets."GeorchestraCustomizations\.py"=config/superset/GeorchestraCustomizations.py \
  --set envFromSecret=geor-demo-sec-superset-secrets \
  --set-file configOverrides.customconfig=config/superset/superset_georchestra_config.py \
  --set configOverrides.secretkey="SECRET_KEY = env('SUPERSET_SECRET_KEY')" \
  --set secretEnv.create=false
```


### Deploying in production

#### SECRET_KEY

A default secret key is included in the command above. For production, you **should** replace it by a key generated on your own.

You can generate such a key with `openssl rand -base64 42`. Then, you will have to either
- place it in the values file or in the `--set` option above
- or you will probably though prefer to provide it in a secret. You can add it in the DB secret, for instance, see above. And then load the environment value in the config file, e.g.: 
`  --set configOverrides.secretkey="SECRET_KEY = env('SUPERSET_SECRET_KEY')"` will append in the config file the instruction to load it from the environment variable.

## Run in Docker
_Reminder: running geOrchestra in production based on the docker-compose file is not recommended. Similarly, for running Superset with geOrchestra using docker, this is more considered as for testing purpose_

In https://github.com/georchestra/docker/, docker-compose.superset.yml will deploy superset on the same network as the geOrchestra composition.

Here are the steps to follow
- Create a user and schema for superset in the geOrchestra DB, as instructed in _Use the geOrchestra applicative database_ above. This can be automated with the command
  ```bash
  docker compose exec database psql -U georchestra -c "CREATE USER superset WITH ENCRYPTED PASSWORD 'superset'; CREATE SCHEMA AUTHORIZATION superset; ALTER ROLE superset SET search_path = superset;"
  ```
- copy into your [georchestra docker folder](https://github.com/georchestra/docker) the following files from this repo:
  - config/ folder (will add a `superset` folder into your config folder)
  - docker/* files into your geOrchestra `docker` folder
- Adjust the config files for superset. You should need only to adapt the `superset_georchestra_config.py` file. 
  - add the connection string lines
  ```yaml
  SQLALCHEMY_DATABASE_URI = "postgresql://superset:superset@database/georchestra"
  REDIS_BASE_URL="redis://redis:6379"
  ```
  - generate and add the [SECRET_KEY](https://superset.apache.org/docs/configuration/configuring-superset/#adding-an-initial-secret_key)

- Run it, adding the `-f docker-compose.superset` option in your `docker compose` command, e.g.
```bash
docker compose -f docker-compose.yml -f docker-compose.override.yml -d docker-compose.superset.yml up -d
```


## Deploy manually

-  Create a user and schema for superset in the geOrchestra DB, as instructed in _Use the geOrchestra applicative database_ above.
- Install Superset: follow https://superset.apache.org/docs/installation/pypi, except that you will install superset itself not from the pipy package but from the git fork: `pip install git+https://github.com/georchestra/superset@a84d2da4d#egg=apache-superset`
- Use the custom config: 
  - copy the config/ folder somewhere in your server
  - configure the pythonpath as described in https://superset.apache.org/docs/configuration/configuring-superset. It needs to be able to access not only the `config/superset_georchestra_config.py` file but also the other `.py` files in this folder
  - Add in superset_georchestra_config.py the connection string to the Postgresql App DB (e.g. `SQLALCHEMY_DATABASE_URI = "postgresql://superset:superset@localhost/georchestra"`)
  - Add in superset_georchestra_config.py the connection string to the redis instanceB (e.g.`REDIS_BASE_URL="redis://localhost:6379"`)
  - generate and add the [SECRET_KEY](https://superset.apache.org/docs/configuration/configuring-superset/#adding-an-initial-secret_key)
- run the app. You can optionally make it a system _service_. Set the `superset_app_root` value to the path prefix you want to server your app on (matching the config in the SP/gateway)

```
gunicorn \
      -w 10 \
      -k gevent \
      --worker-connections 1000 \
      --timeout 120 \
      --limit-request-line 0 \
      --limit-request-field_size 0 \
      -b 127.0.0.1:8088 \
      --access-logfile /var/log/superset/access.log \
      --log-level info \
      --error-logfile /var/log/superset/error.log \
      "superset.app:create_app(superset_app_root='/dash')"
```


## Serve the app behind the Gateway/Security Proxy

This will require only minor changes in the geOrchestra datadir. Depending on the proxy solutions you're using: 

### Security proxy

It should be sufficient to add the corresponding line in the target-mappings.properties file. And restart the SP. 

### Gateway

 - **routes.yaml**:

Add the route defition. Take care to adjust the path prefix and superset host values according to your own context. 

```yaml
spring:
  cloud:
    gateway:
      routes:
      ...
      - id: superset
        uri: ${georchestra.gateway.services.superset.target}
        predicates:
        - Path=/dash/**
georchestra.gateway.services:
  ...
  superset.target: http://${SUPERSET_HOST}:8088/dash/
```

- **gateway.yaml**:
```yaml
georchestra:
  gateway:
    ...
    services:
      ...
      superset:
        target: ${georchestra.gateway.services.superset.target}
```

## Managing users and roles from the geOrchestra console

This is what this integration is meant for !

### User Authentication
The user authentication is read from the `sec-*` HTTP headers provided by the SP/gateway, using Superset's AUTH_REMOTE_USER support.

### Roles
Superset uses roles to define what a user can do, quite similarly with the logic already at play for instance on GeoServer.

What actions are allowed for a given role will still be managed in Superset (by people having an ADMIN role).But the attributions of Superset roles to a user is managed in the console. 

For instance, assigning the `SUPERSET_ADMIN` role to `testadmin` user will give him the Admin profile in Superset. 

Similarly, providing the `SUPERSET_GEO2FRANCE` role to a user will give him the `Geo2france` role in Superset, _provided this role exists in Superset_. The case does not matter, the authentication logic will not care. So the role in Superset can be called geo2france, Geo2france or GEO2FRANCE, it will work the same.

Superset comes with very few roles (Admin, Alpha, Gamma, Public, sql_lab). You will very likely have to add some more roles in Superset with specific ACLs. See https://superset.apache.org/docs/security/#provided-roles about that. Once created, you will assign them to your users _in the console_ the usual way
- create a SUPERSET_SOMETHING role (will match the Superset's `Something` role)
- assign it to your user



