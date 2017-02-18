""" Test plugin for sidecarless plugin manager, local to package.
"""

from yapsy.IPlugin import IPlugin

__plugin_name__ = 'Test Plugin without sidecar file (local to package)'
__plugin_author__ = 'Matt'


class MyPlugin(IPlugin):

    def __init__(self):
        super().__init__()
        print('Initialized no-sidecar plugin (local).')
