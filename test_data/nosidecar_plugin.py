""" Test plugin for one-file plugin manager, separate folder from package.
"""

from yapsy.IPlugin import IPlugin

__plugin_name__ = 'Test plugin without sidecar file (remote)'
__plugin_author__ = 'Matt'


class MyPlugin(IPlugin):

    def __init__(self):
        super().__init__()
        print('Initialized no-sidecar plugin (remote).')
