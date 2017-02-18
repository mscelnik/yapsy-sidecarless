""" Yapsy plugin manager to load a plugin without a side-car file.

By default Yapsy used a side-car ".yapsy-plugin" sidecar file to define what
is (and is not) a valid plugin.  This allows Python modules (files) and
packages (folders) to be loaded agnostically.  However, it also requires you
to create loads of sidecar files!

This module includes three classes to override the Yapsy default classes and to
enable a single Python module to be loaded as a plugin, without a side-car
definition file.  A Python module is considered a plugin if it satisfies these
conditions:

  1. It is a Python file (ends in .py).
  2. It successfully imports into Python.
  3. It contains a module level variable "__plugin_name__".

Because we don't have a sidecar file to hold plugin meta-data, we need to supply
it in the Python module.  We specify the meta-data using double-underscore
module-level variables (all strings):
  __plugin_name__        = The plugin name as identified in Yapsy (required).
  __plugin_author__      = Whoever to blame for the plugin!
  __plugin_version__     = Plugin version number, standard Python format.
  __plugin_website__     = URL for the plugin, if applicable.
  __plugin_description__ = Describe what the plugin does, briefly.
  __plugin_copyright__   = Copyright/licence information.
"""

import yapsy.PluginManager as _managers
import yapsy.PluginFileLocator as _locators

__author__ = "Matthew Celnik"
__copyright__ = "Matthew Celnik"
__licence__ = "LGPL"
__maintainer__ = "Matthew Celnik"
__email__ = "matthew@celnik.co.uk"


class Analyzer(_locators.IPluginFileAnalyzer):
    """ Replacement plugin analyzer to identify and load plugin information.

    This is where the magic happens.  The analyzer determines which files are
    valid plugins, and loads the plugin information.
    """

    def __init__(self):
        super().__init__(name='SingleModuleAnalyzer')

    def _loadModule(self, filepath):
        """ Uses importlib to import a module from a given path.

        Args:
            filename = Path to the module.

        Returns:
            If the file is a valid Python module then returns the module,
            otherwise returns None.
        """
        import importlib.machinery
        import importlib.util

        if filepath.endswith('.py'):
            try:
                loader = importlib.machinery.SourceFileLoader(
                    'testmod', filepath)
                spec = importlib.util.spec_from_loader(loader.name, loader)
                themodule = importlib.util.module_from_spec(spec)
                loader.exec_module(themodule)
                return themodule
            except ImportError:
                return None
        else:
            return None

    def isValidPlugin(self, filename):
        """ Determines if a file is a valid plugin.

        A plugin is valid if:
            #. It is a valid Python module (imports successfully).
            #. It includes module level variable __plugin_name__.

        Args:
            filename = Path to file to test as a plugin.

        Returns:
            If the file is a valid plugin returns True, otherwise False.
        """
        themodule = self._loadModule(filename)
        if themodule is not None:
            name = getattr(themodule, '__plugin_name__', None)
            return name is not None
        else:
            return False

    def getInfosDictFromPlugin(self, dirpath, filename):
        """ Gets plugin information from a valid plugin file.

        Args:
            dirpath = Directory containing the plugin.
            filename = Base file name of the valid plugin.

        Returns:
            To maintain compatibility with Yapsy, this function returns two
            items:
                1. A dictionary containing the plugin information, and
                2. An empty config parser.
            Yapsy expects plugin information to be in a config-formatted text
            file, but of course we don't have that!  It doesn't seem to be a
            problem to return an empty config parser though; the plugins still
            load.
        """
        import os.path
        import configparser
        module_path = os.path.join(dirpath, filename)
        themodule = self._loadModule(module_path)
        infos = {
            # Required plugin info.
            'name': getattr(themodule, '__plugin_name__', ''),
            'path': module_path,
            # Optional plugin info; set default values if missing.
            'author': getattr(themodule, '__plugin_author__', ''),
            'version': getattr(themodule, '__plugin_version__', ''),
            'website': getattr(themodule, '__plugin_website__', ''),
            'copyright': getattr(themodule, '__plugin_copyright__', ''),
            'description': getattr(themodule, '__plugin_description__', ''),
        }
        return infos, configparser.ConfigParser()


class Locator(_locators.PluginFileLocator):
    """ Overrides the base Yapsy file locator to use the single-module analyzer.

    By default this locator uses both the single-module analyzer and the Yapsy
    info file parser.  This is done in the __init__ function, which is all this
    class overrides.
    """

    def __init__(self, analyzers=None):
        # By default use the local analyzer and the plugin file analyzer.
        if analyzers is None:
            analyzers = [
                Analyzer(),
                _locators.PluginFileAnalyzerWithInfoFile("ConfigFileAnalyzer"),
            ]
        super().__init__(analyzers=analyzers)

    def locatePlugins(self):
        """ Walk through the plugins' places and look for plugins. [OVERRIDES]

        This function is a tidied up version from Yapsy.  It differs in that
        the plugin analyzer gets the full file path to check, not just the
        file name.  This allows the single-file analyzer to work.

        Returns:
            The candidate plugins and number of plugins found.
        """
        import os
        import os.path

        _candidates = []
        _discovered = {}

        for directory in map(os.path.abspath, self.plugins_places):
            if not os.path.isdir(directory):
                continue
            if self.recursive:
                debug_txt_mode = "recursively"
                walk_iter = os.walk(directory, followlinks=True)
            else:
                debug_txt_mode = "non-recursively"
                walk_iter = [(directory, [], os.listdir(directory))]

            # Iteratively walk through each directory.
            for root, fldrs, files in walk_iter:
                for filename in files:
                    sidecar_path = os.path.join(root, filename)

                    for analyzer in self._analyzers:
                        # Eliminate the obvious non-plugin files.
                        if not analyzer.isValidPlugin(sidecar_path):
                            continue
                        # Check if we've already discovered this plugin.
                        if sidecar_path in _discovered:
                            continue

                        # Get the plugin info from the candidate file.
                        plugin_info = self._getInfoForPluginFromAnalyzer(
                            analyzer, root, filename)

                        if plugin_info is None:
                            # We consider this was the good strategy to use for:
                            # it failed -> not a plugin -> don't try another
                            # strategy
                            break
                        else:
                            candidate_path = plugin_info.path

                        # Now determine the path of the file to execute,
                        # depending on whether the path indicated is a directory
                        # or a file.  Remember all the files belonging to a
                        # discovered plugin, so that strategies (if several in
                        # use) won't collide
                        if os.path.isdir(candidate_path):
                            # Assume this is a Python package, so the executable
                            # file is the package __init__.py.
                            plugin_path = os.path.join(candidate_path,
                                                       "__init__")

                            # It is a package, so add all the files concerned.
                            for _file in os.listdir(candidate_path):
                                _path = os.path.join(candidate_path, _file)
                                if _file.endswith(".py"):
                                    _discovered[_path] = plugin_path
                        elif ((plugin_info.path.endswith(".py") and
                               os.path.isfile(plugin_info.path)) or
                              os.path.isfile(plugin_info.path + ".py")):
                            # Assume this is a single-module plugin.
                            plugin_path = candidate_path

                            if plugin_path.endswith(".py"):
                                _discovered[plugin_path] = plugin_path[:-3]
                            else:
                                _discovered[plugin_path] = plugin_path
                        else:
                            break
                        _candidates.append((sidecar_path, plugin_path,
                                            plugin_info))
                        _discovered[sidecar_path] = plugin_path
        self._discovered_plugins.update(_discovered)
        return _candidates, len(_candidates)


class Manager(_managers.PluginManager):
    """ Overrides the default Yapsy manager to use the single-module locator.
    """

    def __init__(self,
                 categories_filter=None,
                 directories_list=None,
                 plugin_info_ext=None,
                 plugin_locator=None):

        # By default use the local locator class.
        if plugin_locator is None:
            plugin_locator = Locator()

        super().__init__(
            categories_filter=categories_filter,
            directories_list=directories_list,
            plugin_info_ext=plugin_info_ext,
            plugin_locator=plugin_locator)
