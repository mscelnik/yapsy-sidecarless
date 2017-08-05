import unittest as ut


class BasicPluginTests(ut.TestCase):

    def setUp(self):
        import os.path
        import plugins

        # Use two test plugin locations; local to the package and remote.
        package_fldr = os.path.dirname(plugins.__file__)
        remote_fldr = os.path.join(os.path.dirname(__file__), 'test_data')

        self.mngr = plugins.Manager()
        self.mngr.setPluginPlaces([package_fldr, remote_fldr])
        self.mngr.collectPlugins()

    def test_loaded_four(self):
        """ Loaded exactly five plugins from local directory.
        """
        N = len(self.mngr.getAllPlugins())
        self.assertEqual(N, 5)

    def test_correct_names(self):
        """ Loaded plugin names are correct.
        """
        valid_names = [
            'Test plugin with sidecar file (local)',
            'Test plugin without sidecar file (local)',
            'Test plugin with sidecar file (remote)',
            'Test plugin without sidecar file (remote)',
            'Test plugin without sidecar file that imports module (remote)'
        ]
        for p in self.mngr.getAllPlugins():
            self.assertIn(p.name, valid_names)
