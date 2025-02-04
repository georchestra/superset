# Debugging

## Debugging

This is just a small-ish extension of Superset. You can refer to [Superset Contribute section](https://superset.apache.org/docs/contributing/development) for more information about how to set up a development/debugging installation. Then follow our [manual install section](install-manual.md) to figure out how to activate our customizations. And start your superset instance with a debugging tool (your python IDE, pdb etc).

## Logging

There are at least 2 logging pipes:

### Basic app logging

Basically, the logs are sent to stdout. It is using standard python `logging` package. Cf [config.py ](https://github.com/apache/superset/blob/master/superset/config.py#L66).

You can change the logging config to write to a file by adding in your superset_georchestra_config.py file something like:
```
logging.basicConfig(filename=logname,
                    filemode='a',
                    format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)
```

This is just an example. There are several ways to alter logging. Have a look at 

- [python logging cookbook](https://docs.python.org/3/howto/logging-cookbook.html#logging-cookbook)
- [python logging howto](https://docs.python.org/3/howto/logging.html)

### Event logger

Superset implements a separate logging for all superset events. This is stored in the applicative database (in your `superset` schema). This behaviour is configured in Superset main [config.py ](https://github.com/apache/superset/blob/master/superset/config.py#L82-L86)file and can be changed by overriding the definition in your superset_georchestra_config.py file.


