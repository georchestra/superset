# Preparation

To integrate your Superset deployment into geOrchestra's infrastructure, you will have to make a few changes in your geOrchestra instance:

## Use the geOrchestra applicative database for Superset config (so-called "Metadata DB")

Superset uses a database to store their applicative configuration, they call it the[ "Metadata database"](https://superset.apache.org/docs/installation/architecture#metadata-database). One of the main supported DBMS being Postgresql.

geOrchestra already provides a database for all its apps (not the data. The _applications_ DB): each app is having one dedicated schema. It makes sense to tell Superset to use it for their applicative DB too.

- Create the schema in your geOrchestra DB. Create a dedicated user too, owning this schema. Superset does not manage the selection of the schema, so ou have to set this user's search path to the given schema *only*. Example code:
```
CREATE USER superset WITH ENCRYPTED PASSWORD 'superset';
CREATE SCHEMA superset AUTHORIZATION superset;
ALTER ROLE superset SET search_path = superset;
```
- Tell Superset to use it. Depending on the deployment method, you will have to configure the SQLAlchemy connection string in the config file, or to set some environment variables. Please follow the instructions below for your chosen deployment method.

## Configure routing

Routing to your apps, in geOrchestra, is managed by a routing component: the Security Proxy (will soon be deprecated but not yet) or the Gateway.

This will require only minor changes in the geOrchestra datadir. Depending on the proxy solutions you're using: 

### Security proxy

It should be sufficient to add the corresponding line in the target-mappings.properties file. And restart the SP. 
```
analytic=http://superset_host:8088/analytic/
```
- adjust the host depending on your setup
- 8088 is the default port for Superset
- `/analytic` is the path prefix defined under which you want to access your superset instance. You can change it but take care that both occurences in the line have to match, to simplify proxying. You will also have to use the same values when configuring your Superset deployment (see Install-* sections)

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
        - Path=/analytic/**
georchestra.gateway.services:
  ...
  superset.target: http://superset_host:8088/analytic/
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
        headers:
          proxy: true
          username: true
          roles: true
          email: true
          firstname: true
          lastname: true
```
It is important that the gateway provides at least the username, the roles and the email. First and last names are good to have.