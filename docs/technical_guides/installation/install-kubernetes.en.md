# Deploy using Kubernetes helm chart



The Superset project provides a Helm chart:

- https://github.com/apache/superset/tree/master/helm/superset
- https://superset.apache.org/docs/installation/kubernetes

Following the upstream [Kubernetes install instructions](https://superset.apache.org/docs/installation/kubernetes) are the recommended way. This repo provides you with a *values* file and configuration files and instructions that will allow you to deploy Superset and integrate it into your geOrchestra instance.

*It is assumed that you already have deployed a working geOrchestra instance.*

## Superset custom secret

We will want to make Superset use our geOrchestra *applicative* database to persist its configuration. So, we will disable the shipped-in DB, and instead provide connection parameters to our geOrchestra app database. _Note that you have to [prepare your DB before](preparation.md)_.

The simple and clean way is to publish a *secret* that will replace the default one provided by Superset's helm chart. It has to match an expected structure. We are providing an example in kubernetes/sample-db-secret.yaml. 

Deploy your secret, it will be necessary afterward.

!!! note "Note"

    You might notice we added a `SUPERSET_SECRET_KEY` variable. It will serve to declare the [SECRET_KEY](https://superset.apache.org/docs/configuration/configuring-superset/#adding-an-initial-secret_key) used by Superset to encrypt all sensitive data. You are strongly advised to generate your own (`openssl rand -base64 42`).

## georchestra-values.yaml file

We provide you with an example helm values file in `kubernetes/georchestra-values.yaml`. Here's a lean version of it:
```yaml
extraEnvRaw: 
  - name: SUPERSET_APP_ROOT
    value: "/superset"
  - name: SUPERSET_LOAD_EXAMPLES
    value: "no"
  - name: LOG_LEVEL
    value: "info"
  - name: GUNICORN_KEEPALIVE
    value: "30"
  - name: SERVER_THREADS_AMOUNT
    value: "10"
  - name: SERVER_WORKER_AMOUNT
    value: "10"

secretEnv:
  create: false
  # declare the secret mentioned above

envFromSecret: my-georchestra-custom-superset-secret

image:
  repository: georchestra/superset
  tag: snapshot-20250428-1147-0d6298c29

supersetNode:
  startupProbe: 
    httpGet:
        path: /superset/health
  livenessProbe: 
    httpGet:
        path: /superset/health
  readinessProbe: 
    httpGet:
        path: /superset/health

postgresql:
  # Use geOrchestra's PostgreSQL app DB.
  enabled: false

init:
  # @default -- a script to create admin user and initialize roles
  initscript: |-
    #!/bin/sh
    set -eu
    echo "Upgrading DB schema..."
    superset db upgrade
    if [ -f "/app/configs/georchestra_custom_roles.json" ]; then
      echo "Load the geOrchestra custom roles, including Guest_template"
      superset fab import-roles -p /app/configs/georchestra_custom_roles.json
    fi
    echo "Initializing roles..."
    superset init
    if [ -f "/app/configs/import_datasources.yaml" ]; then
      echo "Importing database connections.... "
      superset import_datasources -p /app/configs/import_datasources.yaml
    fi
```

!!! tip "Tip"

    In this example, /superset is the path to your Superset instance. If you want to change the path, you will have to change the env var but also the path of the probes. And it will always have to match the config you made in the SP/gateway.

This values file will be completed by adding the Superset python config files. Those will be set from external files as they are a bit verbose.

## Superset config files (python files)

There are several config files to load:

- **config/superset/superset_georchestra_config.py** is the main entry point, and this is the one you will be most likely to modify. The provided version makes also use of the following:
- **config/superset/LocalizationFr.py** provides some french locale stuff. It's likely you won't have to change it. If you want to provide support for another locale, you can copy it, adapt it and use your version instead/alongside
- **config/superset/GeorchestraCustomizations.py** provides georchestra-specific logic
    - authentication: rely on REMOTE_USER auth (http sec- headers fed by the gateway/SP)
    - redirection to a custom welcome page
- **config/superset/georchestra_custom_roles.json** provides a `Guest_template` role served to bootstrap the `Public` role (see [making a dashboard Public](../administration/making_a_dashboard_public.en.md#how-to-bootstrap-the-public-role-with-such-permissions)). It is imported by the adapted `initscript` above.

When running your `helm install` command, you will load them with the following options
```
  --set-file extraSecrets."LocalizationFr\.py"=config/superset/LocalizationFr.py \
  --set-file extraSecrets."GeorchestraCustomizations\.py"=config/superset/GeorchestraCustomizations.py \
  --set-file configOverrides.customconfig=config/superset/superset_georchestra_config.py \
  --set-file extraConfigs."georchestra_custom_roles\.json"=config/superset/georchestra_custom_roles.json \
```

## Helm install

Once you have

- prepared your georchestra app DB
- created the DB connection secret
- adjusted the values file
- adjusted the config/superset/superset_georchestra_config.py file

you can deploy using Helm:
```bash
helm upgrade --install -n sup mysuperset superset/superset \
  -f kubernetes/georchestra-values.yaml \
  --set-file extraSecrets."LocalizationFr\.py"=config/superset/LocalizationFr.py \
  --set-file extraSecrets."GeorchestraCustomizations\.py"=config/superset/GeorchestraCustomizations.py \
  --set envFromSecret=geor-demo-sec-superset-secrets \
  --set-file configOverrides.customconfig=config/superset/superset_georchestra_config.py \
  --set-file extraConfigs."georchestra_custom_roles\.json"=config/superset/georchestra_custom_roles.json \
  --set configOverrides.secretkey="SECRET_KEY = env('SUPERSET_SECRET_KEY')"
```

## SECRET_KEY in production

A default secret key is included in the sample secret. For production, you **should** replace it by a key generated on your own.

You can generate such a key with `openssl rand -base64 42`. Then, you will have to either

- place it in the values file or in the `--set` option (`--set configOverrides.secretkey="SECRET_KEY = 'LwAsS+GcbFUbP52NXNwOsG7u3ZJ+LtjGyXlAhhFX7QgwQDD7Zj/IliEe'"`)
- or you will probably though prefer to provide it in a secret. You can add it in the DB secret, for instance, see above. And then load the environment value in the config file, e.g.: 
`  --set configOverrides.secretkey="SECRET_KEY = env('SUPERSET_SECRET_KEY')"` will append in the config file the instruction to load it from the environment variable.