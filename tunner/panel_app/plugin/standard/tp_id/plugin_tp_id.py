import generic_design_patterns as gdp
import yapsy.IPlugin

try:
    import Tkinter as tk
except Exception as e:
    import tkinter as tk


name = "plugin.tp.id"


class Message:
    load_plugin_gui_configuration = "load.plugin.gui.configuration"
    load_plugin_previous_configuration = "load.plugin.previous.configuration"

    add_plugin_to_panel = "add.plugin.to.panel"
    # close_plugin_tp_id_window = "close.plugin.tp.id.window"
    # open_plugin_tp_id_window = "open.plugin.tp.id.window"
    # switch_tp_id_window = "switch.tp_id.window"
    # close_plugins_windows = "close.plugins.windows"
    test_available = "test.available"
    update_variable_value = "update.variable.value"
    test_id_updated = "test.id.updated"

    unsubscribed_message = "unsubscribed.message"


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

    @property
    def gui_items(self):
        return self.tunner.gui.items[name]


class GuiConfigurationLoader(TunnerSubscriber):
    subscription_messages = [Message.load_plugin_gui_configuration]

    def update(self, notification):
        self.tunner.gui.cfg[name] = self.tunner.auto_configuration.load_gui_cfg(__file__)


class StepIDUpdater(TunnerSubscriber):
    subscription_messages = [Message.test_available, Message.test_id_updated]

    def update(self, notification):
        print(self.tunner.variables.get("test.id")["value"])
        self.gui_items["button"].configure(text=self.tunner.variables.get("test.id")["value"])


class PanelAdder(TunnerSubscriber):
    subscription_messages = [Message.add_plugin_to_panel]

    def update(self, notification):
        gui = {}

        self.add_frame(gui)
        self.add_button(gui)

        self.tunner.gui.items[name] = gui

    def add_frame(self, gui):
        gui["frame"] = tk.Frame(self.tunner.gui.panel["frame"])
        gui["frame"].configure(**self.gcfg["plugin"]["frame"]["configure"])
        gui["frame"].grid(**self.gcfg["plugin"]["frame"]["grid"])

    def add_button(self, gui):
        gui["button"] = tk.Button(gui["frame"])
        gui["button"].configure(**self.gcfg["plugin"]["button"]["configure"])
        gui["button"].configure(text=self.tunner.variables.get("test.id")["value"])
        gui["button"].grid(**self.gcfg["plugin"]["button"]["grid"])
        gui["button"].bind("<Button-1>", self.tunner.handler.build(Message.unsubscribed_message))


class TpIdPlugin(yapsy.IPlugin.IPlugin):
    def __init__(self):
        super().__init__()
        self.tunner = None
        self.subscribers_classes = [
            GuiConfigurationLoader,
            PanelAdder,
            StepIDUpdater
        ]

        self.subscribers = []

    def initialize(self, tunner):
        self.tunner = tunner

        for cls in self.subscribers_classes:
            self.subscribers.append(cls(self.tunner))