# Custom setup for a geOrchestra specific instance

# Setup default language
BABEL_DEFAULT_LOCALE = "fr"

# Override the default d3 locale format
# Default values are equivalent to
D3_FORMAT = {
    "decimal": ",",           # - decimal place string (e.g., ".").
    "thousands": " ",         # - group separator string (e.g., ",").
    "grouping": [3],          # - array of group sizes (e.g., [3]), cycled as needed.
    "currency": ["€", "$"]     # - currency prefix/suffix strings (e.g., ["$", ""])
}

# Add custom Geo2France

EXTRA_CATEGORICAL_COLOR_SCHEMES =   [
    {
        "id": 'Geo2FranceDefault',
        "description": '',
        "label": 'Geo2France Default',
        "isDefault": False,
        "colors":
         ['#2f85cd','#7900c4','#f700a6','#ff5754','#ffb255','#fbf752','#8eec46','#b2d9cb']
    },
    {
        "id": 'Geo2FranceAlternative',
        "description": '',
        "label": 'Geo2France Alternative',
        "isDefault": False,
        "colors":
         ['#dfe4ea','#5892ee','#8bc832','#8899a8','#155fd5','#456218','#061d41']
    },
    {
        "id": 'Geo2FranceFull',
        "description": '',
        "label": 'Geo2FranceFull',
        "isDefault": False,
        "colors":
         ['#2f85cd','#7900c4','#f700a6','#ff5754','#ffb255','#fbf752','#8eec46','#b2d9cb','#005fb2','#2900a7','#c6007c','#ff3001','#ff9000','#fee300','#8bc800','#00b966','#6ca6d8','#836ad2','#e370b9','#ff9881','#ffc781','#fff07e','#c1e372','#6ddcaa','#0f4395','#210083','#9f0064','#cd2601','#cd7300','#cdb600','#709f02','#007c48']
    }
]

EXTRA_SEQUENTIAL_COLOR_SCHEMES =  [
    {
        "id": 'Geo2FranceDivergenteSmall',
        "description": '',
        "isDiverging": True,
        "label": 'Geo2france Divergente Basic',
        "isDefault": False,
        "colors":
         ['#8BC832','#3758F9','#3758F9','#061D41']
    },
    {
        "id": 'Geo2FranceDivergenteAlternative',
        "description": '',
        "isDiverging": True,
        "label": 'Geo2france Divergente Alternative',
        "isDefault": False,
        "colors":
         ['#dfe4ea','#0f4395','#d948a5','#061d41']
    },
    {
        "id": 'Geo2FranceDivergente',
        "description": '',
        "isDiverging": True,
        "label": 'Geo2france Divergente',
        "isDefault": False,
        "colors":
         ['#DFE4EA','#8BC832','#3758F9','#061D41']
    },

]