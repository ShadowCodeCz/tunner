import os
import generic_design_patterns as gdp

# TODO: Log plugin
# TODO: Join mode
# TODO: window, dialog, frame cleanup

from . import configuration
from . import variables

try:
    import Tkinter as tk
except Exception as e:
    import tkinter as tk


class Gui:
    def __init__(self):
        self.items = {}
        self.cfg = {}

    @property
    def root(self):
        return self.items["root"]

    @property
    def controller(self):
        return self.items["plugin.panel.controller"]

    @property
    def panel(self):
        return self.items["plugin.panel"]


class Tunner(object):
    def __init__(self):
        self.data = {}
        self.gui = Gui()
        self.provider = gdp.event.Provider()
        self.auto_configuration = configuration.AutoConfiguration()
        self.handler = Handler(self.provider)
        self.variables = variables.Variables(self.data)


class Handler:
    def __init__(self, provider):
        self.provider = provider

    def build(self, message, publisher=None):
        return lambda *args, message=message, publisher=publisher: \
            self.bridge(message, publisher)

    def bridge(self, message, publisher):
        notification = gdp.event.Notification(message, publisher)
        self.provider.notify(notification)


class Plugins:
    def __init__(self):
        self.core = []
        self.standard = []

    @property
    def all(self):
        return self.core + self.standard


class Message:
    load_plugin_previous_configuration = "load.plugin.previous.configuration"
    load_plugin_gui_configuration = "load.plugin.gui.configuration"
    add_core_plugin_widget = "add.core.plugin.widget"
    create_simple_empty_test = "create.empty.simple.test"


class App(object):
    core_plugins_directory = os.path.join("plugin", "core")
    standard_plugins_directory = os.path.join("plugin", "standard")
    plugin_re_pattern = "plugin_.+.py$"

    def __init__(self):
        self.tunner = Tunner()
        self.tunner.gui.items["root"] = tk.Tk()
        self.plugins = Plugins()
        self.core_plugin_collector = gdp.plugin.YapsyRegExPluginCollector([self.core_plugins_directory_path], self.plugin_re_pattern)
        self.standard_plugin_collector = gdp.plugin.YapsyRegExPluginCollector([self.standard_plugins_directory_path], self.plugin_re_pattern)
        self.plugins.core = self.core_plugin_collector.collect()
        self.plugins.standard = self.standard_plugin_collector.collect()

    def run(self):
        self.load_root_gui_configuration()
        self.configure_root_gui()
        self.initialize_plugins()
        self.load_plugins_configuration()
        self.add_core_plugins_widget()
        # self.create_empty_test_steps()
        self.tunner.gui.root.mainloop()

    def initialize_plugins(self):
        for plugin in self.plugins.all:
            plugin.initialize(self.tunner)

    def load_plugins_configuration(self):
        self.load_plugins_gui_configuration()
        self.load_plugins_previous_configuration()

    def load_plugins_previous_configuration(self):
        notification = gdp.event.Notification(Message.load_plugin_previous_configuration)
        self.tunner.provider.notify(notification)

    def load_plugins_gui_configuration(self):
        notification = gdp.event.Notification(Message.load_plugin_gui_configuration)
        self.tunner.provider.notify(notification)

    def add_core_plugins_widget(self):
        notification = gdp.event.Notification(Message.add_core_plugin_widget)
        self.tunner.provider.notify(notification)

    @property
    def standard_plugins_directory_path(self):
        directory_of_this_file = os.path.dirname(__file__)
        return os.path.join(directory_of_this_file, self.standard_plugins_directory)

    @property
    def core_plugins_directory_path(self):
        directory_of_this_file = os.path.dirname(__file__)
        return os.path.join(directory_of_this_file, self.core_plugins_directory)

    def load_root_gui_configuration(self):
        self.tunner.gui.cfg["root"] = self.tunner.auto_configuration.load_gui_cfg(__file__)

    def configure_root_gui(self):
        self.tunner.gui.root.configure(**self.tunner.gui.cfg["root"]["configure"])

    # def create_empty_test_steps(self):
    #     # TODO: Unclean way for simplification of steps_controller
    #     # TODO: Rework
    #     notification = gdp.event.Notification(Message.create_simple_empty_test)
    #     self.tunner.provider.notify(notification)


def run(*args, **kwargs):
    app = App()
    app.run()
