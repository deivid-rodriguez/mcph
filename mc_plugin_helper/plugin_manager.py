"""Module for some plugin-manager methods."""

from os.path import join
from typing import Dict, List, Optional

from yaml import safe_load as parse_yaml

from mc_plugin_helper.config import config
from mc_plugin_helper.file_manager.factory import FileManagerFactory
from mc_plugin_helper.library_manager.factory import LibraryManagerFactory


class Plugin:
    """Create object for plugin.

    Attributes:
        name: Plugin name.
        version: Plugin version.
        last_version: Latest available plugin version.
        file_path: Path to file, where this plugin is.
        update_available: Is update available?
    """

    def __init__(
        self, name: str, version: str, last_version: str, file_path: str, update_available: Optional[bool] = None
    ) -> None:
        """__init__ method.

        Args:
            name: Plugin name.
            version: Plugin version.
            last_version: Latest available plugin version.
            file_path: Path to file, where this plugin is.
            update_available: Is update available?
        """
        self.name = name
        self.version = version
        self.last_version = last_version
        self.file_path = file_path
        self.update_available = (
            PluginManager.is_update_available(version, last_version) if update_available is None else update_available
        )


class PluginManager:
    """Make some stuff with plugin management."""

    def __init__(self, folder: str) -> None:
        """__init__ method.

        Args:
            folder: Folder with plugins.
        """
        self.file_manager = FileManagerFactory.create_file_manager(config["config"]["protocol"])  # type: ignore[arg-type]
        self.library_manager = LibraryManagerFactory.create_library_manager(config["config"]["default_library"])  # type: ignore[arg-type]
        self.plugins_location = folder

    def get_all_plugins(self) -> List[Plugin]:
        """Getter for list with all plugins.

        Returns:
            List with all plugins.
        """
        plugins = []
        for file in self.file_manager.get_all_files(self.plugins_location):
            if not file.endswith(".jar"):
                continue
            parsed_data = self.process_plugin(join(self.plugins_location, file))
            plugins.append(
                Plugin(
                    name=parsed_data["name"],
                    version=str(parsed_data["version"]),
                    last_version=str(self.library_manager.get_latest_version(parsed_data["name"])),
                    file_path=join(self.plugins_location, file),
                ),
            )
        return plugins

    # TODO move to async function
    def process_plugin(self, jar_file) -> Dict[str, str]:
        """Opens plugin.jar and then parsing plugin.yml inside .jar.

        Args:
            jar_file: File object, which points to plugin.

        Returns:
            Parsed yaml in dict.
        """
        plugin_yml = self.file_manager.open_jar(jar_file)
        return parse_yaml(plugin_yml)  # type: ignore[no-any-return]

    @staticmethod
    def is_update_available(version: str, last_version: str) -> Optional[bool]:
        """Checker for plugin, answer on question 'is update available?'.

        Args:
            version: Current plugin version.
            last_version: Last available version.

        Returns:
            True if update available, False if not and None if we can't check.
        """
        if last_version == "Not Found":
            return None
        if (version in last_version) or (last_version in version):
            return False
        return True

    @staticmethod
    def get_specified_plugin(plugin_name: str, plugins: List[Plugin]) -> Optional[Plugin]:
        """Found plugin in list, by its name.

        Args:
            plugin_name: Plugin name of plugin which we try to find.
            plugins: List of plugins, where we need to find.

        Returns:
            Plugin object, or None if we didn't find anything.
        """
        for plugin in plugins:
            if plugin_name == plugin.name:
                return plugin
        return None

    def download_plugin(self, plugin):
        pass
