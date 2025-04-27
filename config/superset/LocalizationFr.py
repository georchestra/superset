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
