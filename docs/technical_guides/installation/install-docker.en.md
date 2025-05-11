# Deploy with docker

The Superset project ships with docker-compose files. We are providing one, in docker/ folder, that is inspired from their docker-compose-image-tag.yml file. 


!!! warning "Warning"
    
    As you might know, running geOrchestra in production based on the docker-compose file is not recommended. 
    Similarly, **running Superset with geOrchestra using docker is more considered as for testing purpose**.


*You are expected to already have a working geOrchestra instance, started from the [geOrchestra docker composition](https://github.com/georchestra/docker)*.  
It is also expected you followed the [preparation steps](preparation.md).

We are going to add the superset compo into this folder, which will make things easier to deploy superset on the same network as the geOrchestra composition.

Here are the steps to follow:

- Create a user and schema for superset in the geOrchestra DB, as instructed in _Use the geOrchestra applicative database_ above. This can be automated with the command
  ```bash
  docker compose exec database psql -U georchestra -c "CREATE USER superset WITH ENCRYPTED PASSWORD 'superset'; CREATE SCHEMA AUTHORIZATION superset; ALTER ROLE superset SET search_path = superset;"
  ```
- copy into your [georchestra docker folder](https://github.com/georchestra/docker) the following files from this repo (_and precisely in this order_):
    - config/ folder (will add a `superset` folder into your config folder)
    - docker/* files into your geOrchestra `docker` folder
- Adjust the config files for superset. You should need only to adapt the `superset_georchestra_config.py` file or `Preconfig.py` (declares the DB connection strings)
    - generate and add the [SECRET_KEY](https://superset.apache.org/docs/configuration/configuring-superset/#adding-an-initial-secret_key)

- Run it, adding the `-f docker-compose.superset` option in your `docker compose` command, e.g.
```bash
docker compose -f docker-compose.yml -f docker-compose.override.yml -d docker-compose.superset.yml up -d
```
- Or you can add it in the `include` section of the main docker-compose.yml:
```yaml
include:
  - ...
  - docker-compose.superset.yml
```
and then simply run `docker compose up -d`
