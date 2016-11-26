import unittest as ut


class BasicPluginTests(ut.TestCase):

    def setUp(self):
        import plugins
        self.mngr = plugins.Manager()
        self.mngr.setPluginPlaces(['.'])
        self.mngr.collectPlugins()

    def test_loaded_two(self):
        """ Loaded exactly two plugins from local directory.
        """
        N = len(self.mngr.getAllPlugins())
        self.assertEqual(N, 2)

    def test_correct_names(self):
        """ Loaded plugin names are correct.
        """
        valid_names = [
            'Example plugin with sidecar file',
            'Example Plugin without sidecar file']
        for p in self.mngr.getAllPlugins():
            if p.name not in valid_names:
                self.fail()
