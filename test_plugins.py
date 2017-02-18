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
        """ Loaded exactly four plugins from local directory.
        """
        N = len(self.mngr.getAllPlugins())
        self.assertEqual(N, 4)

    def test_correct_names(self):
        """ Loaded plugin names are correct.
        """
        valid_names = [
            'Example plugin with sidecar file (local)',
            'Example Plugin without sidecar file (local)',
            'Example plugin with sidecar file (remote)',
            'Example Plugin without sidecar file (remote)',
        ]
        for p in self.mngr.getAllPlugins():
            if p.name not in valid_names:
                self.fail()
