""" Test plugin for one-file plugin manager, separate folder from package,
    that imports another module from the plugin folder.
"""

from yapsy.IPlugin import IPlugin

from nosidecar_with_import_plugin_other_class import OtherClass

__plugin_name__ = 'Test plugin without sidecar file that imports module (remote)'
__plugin_author__ = 'Kevin'


class MyOtherPlugin(IPlugin):

    def __init__(self):
        super().__init__()
        self.other_class = OtherClass()
        print('Initialized no-sidecar plugin with import (remote).')
