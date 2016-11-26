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

    def _loadModule(self, filename):
        """ Uses importlib to import a module from a given path.

        Args:
            filename = Path to the module.

        Returns:
            If the file is a valid Python module then returns the module,
            otherwise returns None.
        """
        import importlib.machinery

        if filename.endswith('.py'):
            try:
                loader = importlib.machinery.SourceFileLoader(
                    'testmod', filename)
                themodule = loader.load_module()
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
