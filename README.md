# yapsy-sidecarless
Override the Yapsy plugin manager to load Python modules as plugins without needing a yapsy-plugin sidecar file.   Also temporarily updates the Python path when loading a plugin so that a given plugin can import modules from the same directory as the main plugin file.

Yapsy plugin manager which loads plugin information from the containing Python
module rather than a yapsy-plugin sidecar file.

See plugins.py module for details.
