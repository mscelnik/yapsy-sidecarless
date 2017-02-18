""" Test plugin for sidecar plugin manager, remote from package.
"""

from yapsy.IPlugin import IPlugin


class MyPlugin(IPlugin):

    def __init__(self):
        super().__init__()
        print('Initialized sidecar plugin (remote).')
