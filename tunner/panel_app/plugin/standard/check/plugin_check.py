import generic_design_patterns as gdp
import yapsy.IPlugin
import flexet
import copy

try:
    import Tkinter as tk
except Exception as e:
    import tkinter as tk


name = "plugin.check"


class Message:
    load_plugin_gui_configuration = "load.plugin.gui.configuration"
    load_plugin_previous_configuration = "load.plugin.previous.configuration"

    add_plugin_to_panel = "add.plugin.to.panel"
    close_plugin_check_window = "close.plugin.check.window"
    open_plugin_check_window = "open.plugin.check.window"
    switch_check_window = "switch.check.window"
    close_plugins_windows = "close.plugins.windows"

    update_flexet_configuration = "update.flexet.configuration"
    write_flexet_configuration = "write.flexet.configuration"

    start_check = "start.check"

    unsubscribed_message = "unsubscribed.message"


class LabeledEntry(object):
    def __init__(self):
        self.frame = None
        self.label = None
        self.label_string = None
        self.entry = None
        self.entry_string = None

    @classmethod
    def build(cls, root, cfg):
        obj = cls()

        obj.frame = tk.Frame(root)
        obj.label_string = tk.StringVar()
        obj.label_string.set(cfg["label"]["text"])
        obj.label = tk.Label(obj.frame, textvariable=obj.label_string)
        obj.label.grid(**cfg["label"]["grid"])
        obj.label.configure(**cfg["label"]["configure"])

        obj.entry_string = tk.StringVar(root)
        obj.entry = tk.Entry(obj.frame, textvariable=obj.entry_string)
        obj.entry.grid(**cfg["entry"]["grid"])
        obj.entry.configure(**cfg["entry"]["configure"])

        obj.frame.grid(**cfg["grid"])
        obj.frame.configure(**cfg["configure"])

        obj.frame.columnconfigure(1, weight=1)
        return obj


class ListBox(object):
    def __init__(self, *args, **kwargs):
        self.frame = None
        self.label = None
        self.text = None

    @classmethod
    def build(cls, root, cfg):
        obj = cls()

        obj.frame = tk.Frame(root)
        obj.label_string = tk.StringVar()
        obj.label_string.set(cfg["label"]["text"])

        obj.label = tk.Label(obj.frame, textvariable=obj.label_string)
        obj.label.grid(**cfg["label"]["grid"])
        obj.label.configure(**cfg["label"]["configure"])

        obj.box = tk.Listbox(obj.frame)
        obj.box.grid(**cfg["listbox"]["grid"])
        obj.box.configure(**cfg["listbox"]["configure"])

        obj.frame.grid(**cfg["grid"])
        obj.frame.configure(**cfg["configure"])

        obj.frame.columnconfigure(1, weight=1)
        return obj


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


class CheckWindowSwitcher(TunnerSubscriber):
    subscription_messages = [Message.switch_check_window]

    def update(self, notification):
        if self.is_open():
            self.send_close_notification()
        else:
            self.send_open_notification()

    def send_open_notification(self):
        notification = gdp.event.Notification(Message.open_plugin_check_window, self)
        self.tunner.provider.notify(notification)

    def send_close_notification(self):
        notification = gdp.event.Notification(Message.close_plugin_check_window, self)
        self.tunner.provider.notify(notification)

    def is_open(self):
        try:
            return self.tunner.gui.items[name]["dialog"] != {}
        except:
            return False


class CheckWindowCloser(TunnerSubscriber):
    subscription_messages = [Message.close_plugin_check_window, Message.close_plugins_windows]

    def update(self, notification):
        if "dialog" in self.tunner.gui.items[name] and self.tunner.gui.items[name]["dialog"] != {}:
            self.write_window_data_to_file()
            self.tunner.gui.items[name]["dialog"]["frame"].destroy()
            self.tunner.gui.items[name]["dialog"] = {}

    def write_window_data_to_file(self):
        notification = gdp.event.Notification(Message.write_flexet_configuration, self)
        self.tunner.provider.notify(notification)


class CheckWindowOpener(TunnerSubscriber):
    subscription_messages = [Message.open_plugin_check_window]

    def update(self, notification):
        gui = {}

        self.create_frame(gui)
        self.set_top_panel(gui)
        self.add_flexet_cfg_entry(gui)
        self.add_start_check_button(gui)
        self.add_listbox(gui)
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

    def add_flexet_cfg_entry(self, gui):
        gui["flexet_cfg_entry"] = LabeledEntry.build(gui["frame"], self.gcfg["dialog"]["flexet_cfg_entry"])
        gui["flexet_cfg_entry"].entry_string.set(self.tunner.data["check.flexet.cfg"])
        gui["flexet_cfg_entry"].entry_string.trace("w", self.tunner.handler.build(Message.update_flexet_configuration, gui["flexet_cfg_entry"]))

    def add_listbox(self, gui):
        gui["listbox"] = ListBox.build(gui["frame"], self.gcfg["dialog"]["listbox"])
        # gui["note"].text.insert(1.0, self.note_text())

    def add_start_check_button(self, gui):
        gui["button_start_check"] = tk.Button(gui["frame"])
        gui["button_start_check"].configure(**self.gcfg["dialog"]["button_start_check"]["configure"])
        gui["button_start_check"].grid(**self.gcfg["dialog"]["button_start_check"]["grid"])
        gui["button_start_check"].bind("<Button-1>", self.tunner.handler.build(Message.start_check))


class Checker(TunnerSubscriber):
    subscription_messages = [Message.start_check]

    def update(self, notification):
        self.tunner.gui.items[name]["dialog"]["listbox"].box.delete(0, tk.END)

        color = {True: "#4DA959", False: "#A94D4D", None: "#A97E4D"}
        for key, value in self.results().items():
            if "test." in key:
                self.tunner.gui.items[name]["dialog"]["listbox"].box.insert('end', key)
                self.tunner.gui.items[name]["dialog"]["listbox"].box.itemconfig('end', foreground=color[value])

    def results(self):
        # return {"test.A": True,
        #         "test.B": False,
        #         "test.C": True,
        #         "test.D": None}
        fn = flexet.build_by_cfg(self.tunner.data["check.flexet.cfg"])
        return fn.run(copy.deepcopy(self.tunner.data))


class FlexetConfigurationTemplateUpdater(TunnerSubscriber):
    subscription_messages = [Message.update_flexet_configuration]

    def update(self, notification):
        self.tunner.data["check.flexet.cfg"] = notification.publisher.entry.get()


class EvidenceDirectoryTemplateWriter(TunnerSubscriber):
    subscription_messages = [Message.write_flexet_configuration]

    def update(self, notification):
        # TODO: second option use self.tunner.data
        content = {
            "check.flexet.cfg": self.tunner.data["check.flexet.cfg"]
        }
        self.tunner.auto_configuration.write_previous_cfg(content, __file__)


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
        gui["button"].bind("<Button-1>", self.tunner.handler.build(Message.switch_check_window))


class CheckPlugin(yapsy.IPlugin.IPlugin):
    def __init__(self):
        super().__init__()
        self.tunner = None
        self.subscribers_classes = [
            GuiConfigurationLoader,
            PreviousConfigurationLoader,
            PanelAdder,
            CheckWindowOpener,
            CheckWindowCloser,
            CheckWindowSwitcher,
            Checker,
            FlexetConfigurationTemplateUpdater,
            EvidenceDirectoryTemplateWriter
        ]

        self.subscribers = []

    def initialize(self, tunner):
        self.tunner = tunner

        for cls in self.subscribers_classes:
            self.subscribers.append(cls(self.tunner))