# Users and roles management

As an app integrated in geOrchestra, it is expected to rely on the console. 

This is exactly what it does. Up to a point, like any other geOrchestra application.

## Users management

It is automatically propagated from the console to superset. 

The user authentication is read from the `sec-*` HTTP headers provided by the SP/gateway, using Superset's AUTH_REMOTE_USER support.

!!! tip "Tip"

    How does it work ? 

    Well, if you want to know the full details, it uses the sec-* HTTP headers provided by your proxy: Security Proxy or Gateway. 
    Actually, for the gateway, it requires that you have told the gateway to provide the expected headers, because it doesn't forward the email address header by default, for instance. See [Gateway documentation](https://github.com/georchestra/georchestra-gateway/blob/main/docs/access-rules.adoc) to see how its done. This is expected to have been done during the deployment (see our Install/Deploy sections).

    The geOrchestra extension to Superset reads the `HTTP_SEC_USERNAME`, `HTTP_SEC_ROLES`, `HTTP_SEC_FIRSTNAME`, `HTTP_SEC_LASTNAME`, `HTTP_SEC_EMAIL` and 
    - creates the user object if it doesn't exist in its database
    - or updates it if it already exists, to handle possible change in the roles



## Roles management

This is the more interesting part.

Superset uses roles to define what a user can do, quite similarly with the logic already at play for instance on GeoServer.

What actions are allowed for a given role will still be managed in Superset (by people having an ADMIN role).But the attributions of Superset roles to a user is managed in the console. 

### In the console

The roles assigned to a user are propagated to Superset. Superset filters out the roles list, and keeps only the superset_related ones. By default (configured in config/superset/superset_georchestra_config.py), it will look out for `SUPERSET_*` roles and keep only the second part. 

For instance, assigning the `SUPERSET_ADMIN` role to `testadmin` user will give him the Admin profile in Superset. 

Similarly, providing the `SUPERSET_GEO2FRANCE` role to a user will give him the `Geo2france` role in Superset, _provided this role exists in Superset_. The letter casing does not matter, the authentication logic will not care. So the role in Superset can be called geo2france, Geo2france or GEO2FRANCE, it will work the same.

Superset comes with very few roles (Admin, Alpha, Gamma, Public, sql_lab). You will very likely have to add some more roles in Superset with specific ACLs. See https://superset.apache.org/docs/security/#provided-roles about that. Once created, you will assign them to your users _in the console_ the usual way

- create a SUPERSET_SOMETHING role (will match the Superset's `Something` role)
- assign it to your user

### In Superset

Well, a bit like what you do with GeoServer, up to this point, a `SUPERSET_SOMETHING` role in the console is _just a label_ passed on to Superset. 

Then it will have to

- match a `Something` role in Superset (you will likely have to create it, unless using only the basic ones, barely sufficient)
- configure, in Superset, what this role is doing (what access rights it is given). Please see [Superset's doc](https://superset.apache.org/docs/security/) for this