""" Example plugin for one-file plugin manager.
"""

from yapsy.IPlugin import IPlugin

__plugin_name__ = 'Example Plugin without sidecar file'
__plugin_author__ = 'Matt'


class MyPlugin(IPlugin):

    def __init__(self):
        super().__init__()
        print('Initialized no-sidecar plugin.')
