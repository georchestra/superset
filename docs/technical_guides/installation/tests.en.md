# Testing



## Healthcheck

Superset provides a healthcheck endpoint  at `/health`. So, supposing you are hosting your superset instance under `analytic` prefix, you can check the app's health at `/superset/health`. The page is expected to display `OK`.

## Checking this geOrchestra integration works as expected

You can check a few things. Let's assume you are hosting your Superset instance under `analytic` prefix.

### Welcome page

`/superset/` should lead you to a quite empty, but working page. You shouldn't get any error.

### Log in as admin

In geOrchestra, create a `SUPERSET_ADMIN` role and assign it to you. 
Then go to `/superset/`. The page should be more feature-rich. It can still be quite empty, if you haven't created any chart or dashboard yet.
But for instance, on the top-right menu, you should be able to list the roles, users, connect to databases etc

![admin menu](images/ss-admin-menu.png)

