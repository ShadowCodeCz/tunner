import os
from PIL import ImageGrab
import datetime
import generic_design_patterns as gdp
import yapsy.IPlugin

try:
    import Tkinter as tk
except Exception as e:
    import tkinter as tk


name = "plugin.print_screen"


class Message:
    load_plugin_gui_configuration = "load.plugin.gui.configuration"
    load_plugin_previous_configuration = "load.plugin.previous.configuration"

    add_plugin_to_panel = "add.plugin.to.panel"
    # close_plugin_print_screen_window = "close.plugin.print.screen.window"
    # open_plugin_print_screen_window = "open.plugin.print.screen.window"
    # switch_print_screen_window = "switch.print.screen.window"
    # close_plugins_windows = "close.plugins.windows"

    make_print_screen = "make.print.screen"
    run_test = "run.test"
    end_test = "end.test"
    update_print_screen_suffix = "update.print.screen.suffix"

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


# class PreviousConfigurationLoader(TunnerSubscriber):
#     subscription_messages = [Message.load_plugin_previous_configuration]
#
#     def update(self, notification):
#         cfg = self.tunner.auto_configuration.load_previous_cfg(__file__)
#
#         for key, value in cfg.items():
#             self.tunner.data[key] = value


# class PrintScreenWindowSwitcher(TunnerSubscriber):
#     subscription_messages = [Message.switch_print_screen_window]
#
#     def update(self, notification):
#         if self.is_open():
#             self.send_close_notification()
#         else:
#             self.send_open_notification()
#
#     def send_open_notification(self):
#         notification = gdp.event.Notification(Message.open_plugin_print_screen_window, self)
#         self.tunner.provider.notify(notification)
#
#     def send_close_notification(self):
#         notification = gdp.event.Notification(Message.close_plugin_print_screen_window, self)
#         self.tunner.provider.notify(notification)
#
#     def is_open(self):
#         try:
#             return self.tunner.gui.items[name]["dialog"] != {}
#         except:
#             return False
#
#
# class PrintScreenWindowCloser(TunnerSubscriber):
#     subscription_messages = [Message.close_plugin_print_screen_window, Message.close_plugins_windows]
#
#     def update(self, notification):
#         if "dialog" in self.tunner.gui.items[name] and self.tunner.gui.items[name]["dialog"] != {}:
#             # self.write_window_data_to_file()
#             self.tunner.gui.items[name]["dialog"]["frame"].destroy()
#             self.tunner.gui.items[name]["dialog"] = {}
#
#
# class PrintScreenWindowOpener(TunnerSubscriber):
#     subscription_messages = [Message.open_plugin_print_screen_window]
#
#     def update(self, notification):
#         gui = {}
#
#         self.create_frame(gui)
#         self.set_top_panel(gui)
#         # self.build_gui(gui)
#
#         self.tunner.gui.items[name] = {}
#         self.tunner.gui.items[name]["dialog"] = gui
#
#     def create_frame(self, gui):
#         gui["frame"] = tk.Toplevel(self.tunner.gui.root)
#         gui["frame"].overrideredirect(True)
#         gui["frame"].configure(**self.gcfg["dialog"]["frame"]["configure"])
#         gui["frame"].columnconfigure(0, weight=1)
#
#     def set_top_panel(self, gui):
#         if self.tunner.gui.cfg["plugin.panel"]["top_panel"]:
#             gui["frame"].geometry('+%d+%d' % (0, self.tunner.gui.root.winfo_reqheight()))
#             gui["frame"].minsize(self.tunner.gui.root.winfo_screenwidth(), 10)
#
#


class PrintScreenSuffixUpdater(TunnerSubscriber):
    subscription_messages = [Message.update_print_screen_suffix]

    def update(self, notification):
        self.tunner.data["print.screen.suffix"] = notification.publisher.get()


class PrintScreenMaker(TunnerSubscriber):
    subscription_messages = [Message.make_print_screen]

    def update(self, notification):
        snapshot = ImageGrab.grab()
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        screens_directory = os.path.join(self.tunner.data["test.run.diectory"], "screens")
        if not os.path.exists(screens_directory):
            os.makedirs(screens_directory)
        if self.tunner.data["print.screen.suffix"] == "":
            path = os.path.join(screens_directory, "monitor_%s.jpg" % ts)
        else:
            path = os.path.join(screens_directory, "monitor_%s_%s.jpg" % (ts, self.tunner.data["print.screen.suffix"]))
        snapshot.save(path)

        self.gui_items["entry"].delete(0, 'end')
        self.tunner.data["print.screen.suffix"] = ""


class PanelAdder(TunnerSubscriber):
    subscription_messages = [Message.add_plugin_to_panel]

    def update(self, notification):
        gui = {}

        self.add_frame(gui)
        self.add_button(gui)
        self.add_entry(gui)

        self.tunner.gui.items[name] = gui

    def add_frame(self, gui):
        gui["frame"] = tk.Frame(self.tunner.gui.panel["frame"])
        gui["frame"].configure(**self.gcfg["plugin"]["frame"]["configure"])
        gui["frame"].grid(**self.gcfg["plugin"]["frame"]["grid"])

    def add_button(self, gui):
        gui["button"] = tk.Button(gui["frame"])
        gui["button"].configure(**self.gcfg["plugin"]["button"]["configure"])
        gui["button"]["state"] = self.tunner.data["_print.screen.button.state"]
        gui["button"].grid(**self.gcfg["plugin"]["button"]["grid"])

        if self.tunner.data["_print.screen.button.state"] == tk.NORMAL:
            gui["button"].bind("<Button-1>", self.tunner.handler.build(Message.make_print_screen))
        else:
            gui["button"].bind("<Button-1>", self.tunner.handler.build(Message.unsubscribed_message))

    def add_entry(self, gui):
        gui["entry_string"] = tk.StringVar()
        gui["entry_string"].trace("w", self.tunner.handler.build(Message.update_print_screen_suffix, gui["entry_string"]))

        gui["entry"] = tk.Entry(gui["frame"], textvariable=gui["entry_string"])
        gui["entry"].grid(**self.gcfg["plugin"]["entry"]["grid"])
        gui["entry"].configure(**self.gcfg["plugin"]["entry"]["configure"])

        gui["entry"].configure(state=self.tunner.data["_print.screen.entry.state"])


class PrintScreenPanelButtonEnabler(TunnerSubscriber):
    subscription_messages = [Message.run_test]

    def update(self, notification):
        self.tunner.data["_print.screen.button.state"] = tk.NORMAL
        self.tunner.gui.items[name]["button"]["state"] = tk.NORMAL
        self.tunner.gui.items[name]["button"].bind("<Button-1>", self.tunner.handler.build(Message.make_print_screen))

        self.tunner.data["_print.screen.entry.state"] = tk.NORMAL
        self.tunner.gui.items[name]["entry"].configure(state=self.tunner.data["_print.screen.entry.state"])


class PrintScreenPanelButtonDisabler(TunnerSubscriber):
    subscription_messages = [Message.end_test]

    def update(self, notification):
        self.tunner.data["_print.screen.button.state"] = tk.DISABLED
        self.tunner.gui.items[name]["button"]["state"] = tk.DISABLED
        self.tunner.gui.items[name]["button"].bind("<Button-1>", self.tunner.handler.build(Message.unsubscribed_message))

        self.tunner.data["_print.screen.entry.state"] = tk.DISABLED
        self.tunner.gui.items[name]["entry"].configure(state=self.tunner.data["_print.screen.entry.state"])


class PrintScreenPlugin(yapsy.IPlugin.IPlugin):
    def __init__(self):
        super().__init__()
        self.tunner = None
        self.subscribers_classes = [
            GuiConfigurationLoader,
            # PreviousConfigurationLoader,
            PanelAdder,
            # PrintScreenWindowOpener,
            # PrintScreenWindowCloser,
            # PrintScreenWindowSwitcher,
            PrintScreenMaker,
            PrintScreenPanelButtonEnabler,
            PrintScreenPanelButtonDisabler,
            PrintScreenSuffixUpdater
        ]

        self.subscribers = []

    def initialize(self, tunner):
        self.tunner = tunner

        for cls in self.subscribers_classes:
            self.subscribers.append(cls(self.tunner))

        self.tunner.data["_print.screen.button.state"] = tk.DISABLED
        self.tunner.data["_print.screen.entry.state"] = tk.DISABLED
        self.tunner.data["print.screen.suffix"] = ""
