# Configuration

Apart from the deployment-specific configuration (see *Deploy* sections), all the configuration will happen in the files stored in this repo's config/ folder.

!!! tip "Tip"

    Superset config files are actually *python* files. which means that not only can we define config values (e.g. `ROW_LIMIT = 5000`) but we can also write functions, classes, override some Superset object and behaviours. You have to do it with caution. But actually, this is how we managed to configure Superset to read users and roles from the geOrchestra console.

- **superset_georchestra_config.py** is the entrypoint for the configuration of your app. This is where you are expected to make most of the changes. See [Configuring Superset](https://superset.apache.org/docs/configuration/configuring-superset#superset_configpy) for more information about what you can do here.  
It is also loading more definitions from the other python files:

    - **GeorchestraCustomizations.py** is where the authentication logic is managed. It also provides a mechanism to configure the home page in Superset. See `HOME_PAGE_VIEW` param in the main config file.

    - **LocalizationFr** adds some config that is specific to French locale (decimal separator, currency). If you want to add support for another locale, just copy it and contribute it. The choice of the file to load from is done in the main config file: `from LocalizationFr import *` actually imports (copies) all the content into the main config file at runtime.