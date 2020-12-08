import generic_design_patterns as gdp
import yapsy.IPlugin

try:
    import Tkinter as tk
except Exception as e:
    import tkinter as tk


name = "plugin.empty"


class Message:
    load_plugin_gui_configuration = "load.plugin.gui.configuration"
    load_plugin_previous_configuration = "load.plugin.previous.configuration"

    add_plugin_to_panel = "add.plugin.to.panel"
    close_plugin_empty_window = "close.plugin.empty.window"
    open_plugin_empty_window = "open.plugin.empty.window"
    switch_empty_window = "switch.empty.window"
    close_plugins_windows = "close.plugins.windows"

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


class GuiConfigurationLoader(TunnerSubscriber):
    subscription_messages = [Message.load_plugin_gui_configuration]

    def update(self, notification):
        self.tunner.gui.cfg[name] = self.tunner.auto_configuration.load_gui_cfg(__file__)


class PreviousConfigurationLoader(TunnerSubscriber):
    subscription_messages = [Message.load_plugin_previous_configuration]

    def update(self, notification):
        cfg = self.tunner.auto_configuration.load_previous_cfg(__file__)

        for key, value in cfg.items():
            self.tunner.data[key] = value


class EmptyWindowSwitcher(TunnerSubscriber):
    subscription_messages = [Message.switch_empty_window]

    def update(self, notification):
        if self.is_open():
            self.send_close_notification()
        else:
            self.send_open_notification()

    def send_open_notification(self):
        notification = gdp.event.Notification(Message.open_plugin_empty_window, self)
        self.tunner.provider.notify(notification)

    def send_close_notification(self):
        notification = gdp.event.Notification(Message.close_plugin_empty_window, self)
        self.tunner.provider.notify(notification)

    def is_open(self):
        try:
            return self.tunner.gui.items[name]["dialog"] != {}
        except:
            return False


class EmptyWindowCloser(TunnerSubscriber):
    subscription_messages = [Message.close_plugin_empty_window, Message.close_plugins_windows]

    def update(self, notification):
        if "dialog" in self.tunner.gui.items[name] and self.tunner.gui.items[name]["dialog"] != {}:
            # self.write_window_data_to_file()
            self.tunner.gui.items[name]["dialog"]["frame"].destroy()
            self.tunner.gui.items[name]["dialog"] = {}


class EmptyWindowOpener(TunnerSubscriber):
    subscription_messages = [Message.open_plugin_empty_window]

    def update(self, notification):
        gui = {}

        self.create_frame(gui)
        self.set_top_panel(gui)
        # self.build_gui(gui)

        self.tunner.gui.items[name] = {}
        self.tunner.gui.items[name]["dialog"] = gui

    def create_frame(self, gui):
        gui["frame"] = tk.Toplevel(self.tunner.gui.root)
        gui["frame"].overrideredirect(True)
        gui["frame"].configure(**self.gcfg["dialog"]["frame"]["configure"])
        gui["frame"].columnconfigure(0, weight=1)

    def set_top_panel(self, gui):
        if self.tunner.gui.cfg["plugin.panel"]["top_panel"]:
            gui["frame"].geometry('+%d+%d' % (0, self.tunner.gui.root.winfo_reqheight()))
            gui["frame"].minsize(self.tunner.gui.root.winfo_screenwidth(), 10)


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
        gui["button"].grid(**self.gcfg["plugin"]["button"]["grid"])
        gui["button"].bind("<Button-1>", self.tunner.handler.build(Message.switch_empty_window))


class EmptyPlugin(yapsy.IPlugin.IPlugin):
    def __init__(self):
        super().__init__()
        self.tunner = None
        self.subscribers_classes = [
            GuiConfigurationLoader,
            PreviousConfigurationLoader,
            PanelAdder,
            EmptyWindowOpener,
            EmptyWindowCloser,
            EmptyWindowSwitcher,
        ]

        self.subscribers = []

    def initialize(self, tunner):
        self.tunner = tunner

        for cls in self.subscribers_classes:
            self.subscribers.append(cls(self.tunner))