# Configuration

Apart from the deployment-specific configuration (see *Deploy* sections), all the configuration will happen in the files stored in this repo's config/ folder.

!!! tip "Tip"

    Superset config files are actually *python* files. which means that not only can we define config values (e.g. `ROW_LIMIT = 5000`) but we can also write functions, classes, override some Superset object and behaviours. You have to do it with caution. But actually, this is how we managed to configure Superset to read users and roles from the geOrchestra console.

- **superset_georchestra_config.py** is the entrypoint for the configuration of your app. This is where you are expected to make most of the changes. See [Configuring Superset](https://superset.apache.org/docs/configuration/configuring-superset#superset_configpy) for more information about what you can do here.  
It is also loading more definitions from the other python files:

    - **Preconfig.py** allows to set some variables that will be necessary for the rest of the configuration , e.g. REDIS_BASE_URL that is not set, when running non-dockerized deployment. This file is loaded at the beginning of superset_georchestra_config.py
    - **GeorchestraCustomizations.py** handles the geOrchestra-specific logic:
        - Manages the authentication logic
        - Provides a mechanism to configure the home page in Superset. See `HOME_PAGE_VIEW` param in the main config file.
        - Loads the configuration for the _geOrchestra header_ (see below)
    - **LocalizationFr.py** adds some config that is specific to French locale (decimal separator, currency). If you want to add support for another locale, just copy it and contribute it.  
    The choice of the file to load from is done in the main config file: `from LocalizationFr import *` actually imports (copies) all the content into the main config file at runtime.  
    **_You need to have built Superset with i18n support for both frontend and backend_**.
    - **Overrides.py** can be used to override anything previously defined. If not useful to you, you can even delete this file.


## Configuring the geOrchestra header

The header is the top menu usually added to all geOrchestra components.

There are two ways to configure the header:

- either by reading the geOrchestra default.properties file. The `GEORCHESTRA_PROPERTIES_FILE_PATH` config parameter needs to point to the properties file (local path. URLs are not supported).
- or by providing the necessary config parameters directly into your [superset configuration files](https://github.com/georchestra/superset/blob/main/config/superset/superset_georchestra_config.py#L52).

If both are provided, the values from the superset config file will override the ones from the default.properties file.

!!! tip "Tip"

    If you don't want the header displayed on the superset app, it is possible to disable it with the config parameter `GEORCHESTRA_NOHEADER=True`.

### Adding a Superset entry in the header menu

The items of the geOrchestra header are now entirely configurable, [since January 2025](https://github.com/georchestra/header/commit/381da5833cb4426ad45210d479e77f9e1f721ecc). You can find a sample config-file [here](https://github.com/georchestra/superset/blob/main/extras/header-config.json). 

The path to the config file will need to be an URL (relative or absolute, but since this will be loaded by javascript, it cannot be a local path).
