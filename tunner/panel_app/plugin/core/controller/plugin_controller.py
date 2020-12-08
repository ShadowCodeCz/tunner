import os
import datetime
import generic_design_patterns as gdp
import yapsy.IPlugin

try:
    import Tkinter as tk
except Exception as e:
    import tkinter as tk


name = "plugin.panel.controller"


class Message:
    load_plugin_gui_configuration = "load.plugin.gui.configuration"
    switch_plugin_panel = "switch.plugin.panel"
    add_core_plugin_widget = "add.core.plugin.widget"


class TunnerSubscriber(gdp.event.AdvancedSubscriber):
    subscription_messages = []

    def __init__(self, tunner):
        super().__init__(tunner.provider)
        self.tunner = tunner
        for message in self.subscription_messages:
            self.subscribe(message)

    @property
    def gcfg(self):
        return self.tunner.gui.cfg[name]


class LoadGuiConfiguration(TunnerSubscriber):
    subscription_messages = [Message.load_plugin_gui_configuration]

    def update(self, notification):
        self.tunner.gui.cfg[name] = self.tunner.auto_configuration.load_gui_cfg(__file__)


class AddPluginWidgetToTunner(TunnerSubscriber):
    subscription_messages = [Message.add_core_plugin_widget]

    def update(self, notification):
        gui = {}

        self.add_frame(gui)
        self.add_button(gui)
        self.set_top_panel(gui)

        self.tunner.gui.items[name] = gui

    def add_frame(self, gui):
        gui["frame"] = tk.Frame(self.tunner.gui.root)
        gui["frame"].configure(**self.gcfg["plugin"]["frame"]["configure"])
        gui["frame"].grid(**self.gcfg["plugin"]["frame"]["grid"])

    def add_button(self, gui):
        gui["button"] = tk.Button(gui["frame"])
        gui["button"].configure(**self.gcfg["plugin"]["button"]["configure"])
        gui["button"].grid(**self.gcfg["plugin"]["button"]["grid"])
        gui["button"].bind("<Button-1>", self.tunner.handler.build(Message.switch_plugin_panel))

    def set_top_panel(self, gui):
        # TODO: Move values to gui.json
        if self.gcfg["top_panel"]:
            self.tunner.gui.root.overrideredirect(True)
            self.tunner.gui.root.geometry('+%d+%d' % (0, 0))
            # self.tunner.gui.root.minsize(gui["frame"].winfo_reqwidth(), 10)
            #TODO: fix value rework
            self.tunner.gui.root.minsize(25, 10)
            self.tunner.gui.root.attributes('-topmost', True)


class ControllerPlugin(yapsy.IPlugin.IPlugin):
    def __init__(self):
        super().__init__()
        self.tunner = None
        self.subscribers_classes = [
            LoadGuiConfiguration,
            AddPluginWidgetToTunner,
            # WindowManager,
        ]

        self.subscribers = []

    def initialize(self, tunner):
        self.tunner = tunner

        for cls in self.subscribers_classes:
            self.subscribers.append(cls(self.tunner))