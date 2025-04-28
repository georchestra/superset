# Deploy manually

*You are expected to already have a working geOrchestra instance, started from the [geOrchestra docker composition](https://github.com/georchestra/docker).*
*It is also expected you followed the [preparation steps](preparation.md).

-  Create a user and schema for superset in the geOrchestra DB, as instructed in _Use the geOrchestra applicative database_ above.
- Install Superset: follow https://superset.apache.org/docs/installation/pypi, except that you will install superset itself not from the pipy package but from the git fork: `pip install git+https://github.com/georchestra/superset@a84d2da4d#egg=apache-superset`
- Use the custom config: 
    - copy the config/ folder somewhere in your server
    - configure the pythonpath as described in https://superset.apache.org/docs/configuration/configuring-superset. It needs to be able to access not only the `config/superset_georchestra_config.py` file but also the other `.py` files in this folder
    - Add in superset_georchestra_config.py the connection string to the Postgresql App DB (e.g. `SQLALCHEMY_DATABASE_URI = "postgresql://superset:superset@localhost/georchestra"`)
    - Add in superset_georchestra_config.py the connection string to the redis instanceB (e.g.`REDIS_BASE_URL="redis://localhost:6379"`)
    - generate and add the [SECRET_KEY](https://superset.apache.org/docs/configuration/configuring-superset/#adding-an-initial-secret_key)
    - you will probably want to read [making a dashboard Public](../administration//making_a_dashboard_public.en.md#how-to-bootstrap-the-public-role-with-such-permissions) and import the `Guest_template` role before running the app. Or disable the line `PUBLIC_ROLE_LIKE = "Guest_template"` in [superset_georchestra_config.py](https://github.com/georchestra/superset/blob/main/config/superset/superset_georchestra_config.py#L76)
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
      "superset.app:create_app(superset_app_root='/superset')"
```