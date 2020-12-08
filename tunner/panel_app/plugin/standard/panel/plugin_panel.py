import os
import datetime
import generic_design_patterns as gdp
import yapsy.IPlugin

try:
    import Tkinter as tk
except Exception as e:
    import tkinter as tk


name = "plugin.panel"


class Message:
    load_plugin_gui_configuration = "load.plugin.gui.configuration"
    switch_plugin_panel = "switch.plugin.panel"
    add_core_plugin_widget = "add.core.plugin.widget"
    close_plugin_panel = "close.plugin.panel"
    open_plugin_panel = "open.plugin.panel"
    add_plugin_to_panel = "add.plugin.to.panel"
    close_plugins_windows = "close.plugins.windows"


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


# class CloseEvidenceDirectoryWindow(TunnerSubscriber):
#     subscription_message = "close.evidence.directory.window"
#
#     def update(self, notification):
#         self.tunner.gui.items["starter"]["dialog"]["frame"].destroy()
#         self.tunner.gui.items["starter"]["dialog"] = {}

#
# class WindowManager(TunnerSubscriber):
#     subscription_message = "switch.evidence.directory.window"
#     is_open = False
#
#     def update(self, notification):
#         if self.is_open:
#             self.is_open = False
#             notification = gdp.event.Notification("close.evidence.directory.window", self)
#             self.tunner.provider.notify(notification)
#         else:
#             self.is_open = True
#             notification = gdp.event.Notification("start.evidence.directory.window", self)
#             self.tunner.provider.notify(notification)

class PanelWindowSwitcher(TunnerSubscriber):
    subscription_messages = [Message.switch_plugin_panel]
    visible = False

    def update(self, notification):
        if self.visible:
            self.send_close_notification()
            self.visible = False
        else:
            self.send_open_notification()
            self.visible = True

    def send_open_notification(self):
        notification = gdp.event.Notification(Message.open_plugin_panel, self)
        self.tunner.provider.notify(notification)

    def send_close_notification(self):
        notification = gdp.event.Notification(Message.close_plugin_panel, self)
        self.tunner.provider.notify(notification)


class PanelWindowCloser(TunnerSubscriber):
    subscription_messages = [Message.close_plugin_panel]

    def update(self, notification):
        self.tunner.gui.items[name]["frame"].destroy()
        self.tunner.gui.items[name] = {}

        notification = gdp.event.Notification(Message.close_plugins_windows)
        self.tunner.provider.notify(notification)


class PanelWindowOpener(TunnerSubscriber):
    subscription_messages = [Message.open_plugin_panel]

    def update(self, notification):
        gui = {}

        self.add_frame(gui)
        self.set_top_panel(gui)

        self.tunner.gui.items[name] = gui

        self.add_plugins_widgets()

    def add_frame(self, gui):
        gui["frame"] = tk.Toplevel(self.tunner.gui.root)
        gui["frame"].configure(**self.gcfg["plugin"]["frame"]["configure"])
        # gui["frame"].grid(**self.gcfg["plugin"]["frame"]["grid"])

    @property
    def button_handler(self):
        return lambda event, message=Message.switch_plugin_panel, publisher=None: self.tunner.bridge(event, message, publisher)

    def set_top_panel(self, gui):
        # TODO: Move values to gui.json
        if self.gcfg["top_panel"]:
            gui["frame"].overrideredirect(True)
            # print(self.tunner.gui.controller["frame"].winfo_reqwidth())
            # print(self.tunner.gui.root.winfo_reqwidth())
            # TODO: fix value rework
            gui["frame"].geometry('+%d+%d' % (25, 0))
            gui["frame"].minsize(self.tunner.gui.root.winfo_screenwidth() - self.tunner.gui.controller["frame"].winfo_reqwidth(), 10)
            gui["frame"].attributes('-topmost', True)

    def add_plugins_widgets(self):
        notification = gdp.event.Notification(Message.add_plugin_to_panel)
        self.tunner.provider.notify(notification)


class PanelPlugin(yapsy.IPlugin.IPlugin):
    def __init__(self):
        super().__init__()
        self.tunner = None
        self.subscribers_classes = [
            LoadGuiConfiguration,
            PanelWindowOpener,
            PanelWindowCloser,
            PanelWindowSwitcher
            # WindowManager,
        ]

        self.subscribers = []

    def initialize(self, tunner):
        self.tunner = tunner

        for cls in self.subscribers_classes:
            self.subscribers.append(cls(self.tunner))