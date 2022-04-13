"""Module for CLI commands."""

from typing import List, Optional, Union

from click import Path, argument, command, echo
from prettytable import PrettyTable

from mc_plugin_helper.config import Config, config
from mc_plugin_helper.models.plugin import Plugin
from mc_plugin_helper.plugin_manager import PluginManager


class CLI:
    """Class for CLI interface. Do not forget add commands to __main__.py!"""

    @staticmethod
    @command()
    @argument("plugin_name", type=str, default="all")
    @argument("folder", type=Path(exists=True), required=False)
    def check(plugin_name: str, folder: Union[str, None]) -> None:
        """Check updates for plugin or all plugins.

        Args:
            folder: Folder with plugins.
                If nothing passing, check in config.
                If passed something, check all .jar files in folder.
            plugin_name: Plugin name to check, or just "all".
        """
        if folder is None:
            folder = config["config"]["plugins-path"]

        plugin_manager = PluginManager(folder)
        plugins = plugin_manager.get_all_plugins()
        plugin = plugin_manager.get_specified_plugin(plugin_name, plugins)

        if plugin_name == "all":
            NiceEcho.nice_echo_plugins(plugins)
        elif plugin is None:
            echo("Plugin not installed!")
        else:
            NiceEcho.nice_echo_plugins([plugin])

    @staticmethod
    @command()
    @argument("name", type=str)
    @argument("value", type=str, required=False)
    def config(name: str, value: Optional[str]) -> None:
        """Allow changing config without editing it manually.

        Args:
            name: Parameter name to edit. Need to be in format ``section.name``.
            value: Value to set. If not set, we will just show value.
        """
        try:
            section, name = name.split(".")
        except ValueError:
            return echo("Parameter `name` need to be in format `section.name`")
        if section not in config:
            return echo("Section not exists!")
        if name not in config[section]:
            return echo("Parameter not exists!")

        config_render = """[{0}]\n{1} = {2}"""

        if value is None:
            return echo(config_render.format(section, name, config.get(section, name)))

        echo("Value before: " + config.get(section, name))
        echo("Changing config to:\n" + config_render.format(section, name, value))

        config.set(section, name, value)
        Config(config).update_config()


class NiceEcho:
    """Class for Nice Echo some info, to console."""

    @staticmethod
    def style_table(table: PrettyTable) -> None:
        """Add some style options to table argument.

        Args:
            table: Table which we need change.
        """
        table.vertical_char = "│"
        table.horizontal_char = "─"
        table.top_junction_char = "─"
        table.bottom_junction_char = "─"
        table.top_right_junction_char = "┐"
        table.top_left_junction_char = "┌"
        table.bottom_left_junction_char = "└"
        table.bottom_right_junction_char = "┘"

    @staticmethod
    def nice_echo_plugins(plugins: List[Plugin]) -> None:
        """Nice echo all plugins from a list.

        Args:
            plugins: List with plugins objects with information about it.
        """
        if len(plugins) == 0:
            echo("No plugins found!")
            return

        table = PrettyTable()
        NiceEcho.style_table(table)
        table.field_names = ["Num", "Name", "Current Version", "Last Version", "Update Available"]

        i = 1
        for plugin in plugins:
            table.add_row([i, plugin.name, plugin.version, plugin.last_version, plugin.update_available])
            i += 1

        echo(table)
