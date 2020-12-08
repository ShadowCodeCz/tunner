import os
import datetime
import alphabetic_timestamp as ats
import generic_design_patterns as gdp
import yapsy.IPlugin

try:
    import Tkinter as tk
except Exception as e:
    import tkinter as tk


name = "plugin.start"


class Message:
    load_plugin_gui_configuration = "load.plugin.gui.configuration"
    add_plugin_to_panel = "add.plugin.to.panel"
    close_plugin_start_window = "close.plugin.start.window"
    open_plugin_start_window = "open.plugin.start.window"
    load_plugin_previous_configuration = "load.plugin.previous.configuration"
    switch_start_window = "switch.start.window"
    close_plugins_windows = "close.plugins.windows"
    update_evidence_directory_template = "update.evidence.directory.template"
    write_evidence_directory_template = "write.evidence.directory.template"
    run_test = "run.test"
    end_test = "end.test"
    prepare_test_run = "prepare.test.run"
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


class StartWindowSwitcher(TunnerSubscriber):
    subscription_messages = [Message.switch_start_window]
    # visible = False

    def update(self, notification):
        if self.is_open():
            self.send_close_notification()
            # self.visible = False
        else:
            self.send_open_notification()
            # self.visible = True

    def send_open_notification(self):
        notification = gdp.event.Notification(Message.open_plugin_start_window, self)
        self.tunner.provider.notify(notification)

    def send_close_notification(self):
        notification = gdp.event.Notification(Message.close_plugin_start_window, self)
        self.tunner.provider.notify(notification)

    def is_open(self):
        try:
            return self.tunner.gui.items[name]["dialog"] != {}
        except:
            return False


class StartWindowCloser(TunnerSubscriber):
    subscription_messages = [Message.close_plugin_start_window, Message.close_plugins_windows]

    def update(self, notification):
        if "dialog" in self.tunner.gui.items[name] and self.tunner.gui.items[name]["dialog"] != {}:
            self.write_window_data_to_file()
            self.tunner.gui.items[name]["dialog"]["frame"].destroy()
            self.tunner.gui.items[name]["dialog"] = {}

    def write_window_data_to_file(self):
        notification = gdp.event.Notification(Message.write_evidence_directory_template, self)
        self.tunner.provider.notify(notification)


class TestRunPreparer(TunnerSubscriber):
    subscription_messages = [Message.prepare_test_run]

    def update(self, notification):
        self.create_test_run_directory(notification)
        self.close_window()
        self.start_test_run()

    def create_test_run_directory(self, notification):
        specific_time = datetime.datetime.now()
        # template = self.tunner.gui.items["starter"]["dialog"]["directory_entry"].entry.get()
        template = notification.publisher.entry_string.get()
        directory_path = specific_time.strftime(template)

        self.tunner.data["test.run.start.time"] = specific_time
        self.tunner.data["test.run.diectory"] = directory_path

        # TODO: handle exceptions
        os.makedirs(directory_path, exist_ok=True)

    def close_window(self):
        notification = gdp.event.Notification(Message.close_plugin_start_window, self)
        self.tunner.provider.notify(notification)

    def start_test_run(self):
        notification = gdp.event.Notification(Message.run_test, self)
        self.tunner.provider.notify(notification)


class EvidenceDirectoryTemplateWriter(TunnerSubscriber):
    subscription_messages = [Message.write_evidence_directory_template]

    def update(self, notification):
        # TODO: second option use self.tunner.data
        content = {
            "evidence.directory.template": self.tunner.gui.items[name]["dialog"]["directory_entry"].entry_string.get()
        }
        self.tunner.auto_configuration.write_previous_cfg(content, __file__)


class EvidenceDirectoryTemplateUpdater(TunnerSubscriber):
    subscription_messages = [Message.update_evidence_directory_template]

    def update(self, notification):
        self.tunner.data["evidence.directory.template"] = notification.publisher.entry.get()


class StartWindowOpener(TunnerSubscriber):
    subscription_messages = [Message.open_plugin_start_window]

    def update(self, notification):
        gui = {}

        self.create_frame(gui)
        self.set_top_panel(gui)
        self.build_gui(gui)

        self.tunner.gui.items[name]["dialog"] = gui

    def create_frame(self, gui):
        gui["frame"] = tk.Toplevel(self.tunner.gui.root)
        gui["frame"].overrideredirect(True)
        gui["frame"].configure(**self.gcfg["dialog"]["frame"]["configure"])
        gui["frame"].columnconfigure(0, weight=1)

    def set_top_panel(self, gui):
        if self.tunner.gui.cfg["plugin.panel"]["top_panel"]:
            gui["frame"].geometry('+%d+%d' % (0, self.tunner.gui.root.winfo_reqheight()))
            gui["frame"].minsize(self.tunner.gui.root.winfo_screenwidth(), self.tunner.gui.root.winfo_reqheight())

    def build_gui(self, gui):
        self.add_directory_entry(gui)
        self.add_start_tr_button(gui)

    def add_directory_entry(self, gui):
        gui["directory_entry"] = LabeledEntry.build(gui["frame"], self.gcfg["dialog"]["directory_entry"])
        gui["directory_entry"].entry_string.set(self.tunner.data["evidence.directory.template"])
        gui["directory_entry"].entry_string.trace("w", self.tunner.handler.build(Message.update_evidence_directory_template, gui["directory_entry"]))

    def add_start_tr_button(self, gui):
        gui["start_tr_button"] = tk.Button(gui["frame"])
        gui["start_tr_button"].configure(**self.gcfg["dialog"]["button_start_test_run"]["configure"])
        gui["start_tr_button"].grid(**self.gcfg["dialog"]["button_start_test_run"]["grid"])
        gui["start_tr_button"].bind("<Button-1>", self.tunner.handler.build(Message.prepare_test_run, gui["directory_entry"]))


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
        gui["button"]["state"] = self.tunner.data["_start.button.state"]
        gui["button"].grid(**self.gcfg["plugin"]["button"]["grid"])

        if self.tunner.data["_start.button.state"] == tk.NORMAL:
            gui["button"].bind("<Button-1>", self.tunner.handler.build(Message.switch_start_window))
        else:
            gui["button"].bind("<Button-1>", self.tunner.handler.build(Message.unsubscribed_message))
            start_time = self.tunner.data["test.run.start.time"]
            test_run_alphabetic_ts = ats.base62.from_datetime(start_time, time_unit=ats.TimeUnit.seconds)
            gui["button"].configure(text=test_run_alphabetic_ts)


class StartPanelButtonEnabler(TunnerSubscriber):
    subscription_messages = [Message.end_test]

    def update(self, notification):
        self.tunner.data["_start.button.state"] = tk.NORMAL
        self.tunner.gui.items[name]["button"]["state"] = tk.NORMAL
        self.tunner.gui.items[name]["button"].bind("<Button-1>", self.tunner.handler.build(Message.switch_start_window))
        self.tunner.gui.items[name]["button"].configure(text="Start Test Run")


class StartPanelButtonDisabler(TunnerSubscriber):
    subscription_messages = [Message.run_test]

    def update(self, notification):
        self.tunner.data["_start.button.state"] = tk.DISABLED
        self.tunner.gui.items[name]["button"]["state"] = tk.DISABLED
        self.tunner.gui.items[name]["button"].bind("<Button-1>", self.tunner.handler.build(Message.unsubscribed_message))

        start_time = self.tunner.data["test.run.start.time"]
        test_run_alphabetic_ts = ats.base62.from_datetime(start_time, time_unit=ats.TimeUnit.seconds)
        self.tunner.gui.items[name]["button"].configure(text=test_run_alphabetic_ts)


class StartPlugin(yapsy.IPlugin.IPlugin):
    def __init__(self):
        super().__init__()
        self.tunner = None
        self.subscribers_classes = [
            GuiConfigurationLoader,
            PreviousConfigurationLoader,
            PanelAdder,
            StartWindowOpener,
            StartWindowCloser,
            StartWindowSwitcher,
            TestRunPreparer,
            EvidenceDirectoryTemplateUpdater,
            EvidenceDirectoryTemplateWriter,
            StartPanelButtonEnabler,
            StartPanelButtonDisabler
        ]

        self.subscribers = []

    def initialize(self, tunner):
        self.tunner = tunner

        for cls in self.subscribers_classes:
            self.subscribers.append(cls(self.tunner))

        self.tunner.data["_start.button.state"] = tk.NORMAL