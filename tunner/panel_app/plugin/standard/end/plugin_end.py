import os
import datetime

import json
import uuid
import socket
import time
import platform
import alphabetic_timestamp as ats
import generic_design_patterns as gdp
import yapsy.IPlugin

try:
    import Tkinter as tk
except Exception as e:
    import tkinter as tk


name = "plugin.end"


class Message:
    load_plugin_gui_configuration = "load.plugin.gui.configuration"
    load_plugin_previous_configuration = "load.plugin.previous.configuration"

    add_plugin_to_panel = "add.plugin.to.panel"
    close_plugin_end_window = "close.plugin.end.window"
    open_plugin_end_window = "open.plugin.end.window"
    switch_end_window = "switch.end.window"
    close_plugins_windows = "close.plugins.windows"

    update_end_status_note = "update.end.status.note"
    update_end_status = "update.end.status"

    write_end_data = "write.end.data"

    write_tunner_file = "write.tunner.file"
    end_test = "end.test"
    run_test = "run.test"

    unsubscribed_message = "unsubscribed.message"


class Note(object):
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

        obj.text = tk.Text(obj.frame)
        obj.text.grid(**cfg["text"]["grid"])
        obj.text.configure(**cfg["text"]["configure"])

        obj.frame.grid(**cfg["grid"])
        obj.frame.configure(**cfg["configure"])

        obj.frame.columnconfigure(1, weight=1)
        return obj


class LabeledOptionMenu(object):
    def __init__(self, *args, **kwargs):
        self.frame = None
        self.label = None
        self.option_variable = None
        self.option_menu = None

    @classmethod
    def build(cls, root, cfg):
        obj = cls()

        obj.frame = tk.Frame(root)
        obj.label_string = tk.StringVar()
        obj.label_string.set(cfg["label"]["text"])

        obj.label = tk.Label(obj.frame, textvariable=obj.label_string)
        obj.label.grid(**cfg["label"]["grid"])
        obj.label.configure(**cfg["label"]["configure"])

        obj.option_variable = tk.StringVar()
        obj.option_variable.set(cfg["option_menu"]["options_list"][0])
        obj.option_menu = tk.OptionMenu(obj.frame, obj.option_variable, *cfg["option_menu"]["options_list"])
        obj.option_menu.grid(**cfg["option_menu"]["grid"])
        obj.option_menu.configure(**cfg["option_menu"]["configure"])

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


class EndWindowSwitcher(TunnerSubscriber):
    subscription_messages = [Message.switch_end_window]
    # visible = False

    def update(self, notification):
        if self.is_open():
            self.send_close_notification()
            # self.visible = False
        else:
            self.send_open_notification()
            # self.visible = True

    def send_open_notification(self):
        notification = gdp.event.Notification(Message.open_plugin_end_window, self)
        self.tunner.provider.notify(notification)

    def send_close_notification(self):
        notification = gdp.event.Notification(Message.close_plugin_end_window, self)
        self.tunner.provider.notify(notification)

    def is_open(self):
        try:
            return self.tunner.gui.items[name]["dialog"] != {}
        except:
            return False


class TunnerFileContentGenerator(object):
    def __init__(self, data):
        self.data = data

    def generate(self, start_time, end_time):
        return {
            "id": ats.base62.from_datetime(start_time, time_unit=ats.TimeUnit.seconds),

            "time": {
                "zone": str(time.tzname),
                "start": {
                    "str": str(start_time),
                    "epoch": start_time.timestamp(),

                },
                "end": {
                    "str": str(end_time),
                    "epoch": end_time.timestamp(),
                }
            },

            "last_update": end_time.timestamp(),

            "environment": {
                "platform": {
                    "machine": platform.machine(),
                    "node": platform.node(),
                    "processor": platform.processor(),
                    "release": platform.release(),
                    "system": platform.system(),
                    "version": platform.version(),
                },
                "network": {
                    "host": socket.gethostbyname(socket.gethostname()),
                    "mac": uuid.getnode()
                }
            },

            "variables": self.data["variables"],
            "comments": self.data["comments"],

            "notes": {
                "tr": self.data["tr.note"],
                "tp": self.data["tp.note"],
            },

            "test": self.data["test"],

            "results": [
                {
                    "status": self.data["end.status"],
                    "note": self.data["end.status.note"]
                }
            ]

        }

# TODO: Move it to separate plugin without GUI
class TunnerFileWriter(TunnerSubscriber):
    subscription_messages = [Message.write_tunner_file, Message.run_test]

    def update(self, notification):
        start_time = self.tunner.data["test.run.start.time"]
        end_time = datetime.datetime.now()

        generator = TunnerFileContentGenerator(self.tunner.data)
        content = generator.generate(start_time, end_time)

        self.write_tunner_file(content)

    def write_tunner_file(self, content):
        with open(self._tunner_file_path(), "w+", encoding='utf8') as f:
            json.dump(content, f, indent=4, sort_keys=True)

    def _tunner_file_path(self):
        return os.path.join(self.tunner.data["test.run.diectory"], ".tunner")


class TestRunEnder(TunnerSubscriber):
    subscription_messages = [Message.end_test]

    def update(self, notification):
        self.send_write_to_tunner_file()
        self.send_close_notification()

    def send_write_to_tunner_file(self):
        notification = gdp.event.Notification(Message.write_tunner_file)
        self.tunner.provider.notify(notification)

    def send_close_notification(self):
        notification = gdp.event.Notification(Message.close_plugin_end_window, self)
        self.tunner.provider.notify(notification)


class EndWindowCloser(TunnerSubscriber):
    subscription_messages = [Message.close_plugin_end_window, Message.close_plugins_windows]

    def update(self, notification):
        if "dialog" in self.tunner.gui.items[name] and self.tunner.gui.items[name]["dialog"] != {}:
            self.write_window_data_to_file()
            self.tunner.gui.items[name]["dialog"]["frame"].destroy()
            self.tunner.gui.items[name]["dialog"] = {}

    def write_window_data_to_file(self):
        notification = gdp.event.Notification(Message.write_end_data, self)
        self.tunner.provider.notify(notification)


class EndWindowOpener(TunnerSubscriber):
    subscription_messages = [Message.open_plugin_end_window]

    def update(self, notification):
        gui = {}

        self.create_frame(gui)
        self.set_top_panel(gui)
        # self.build_gui(gui)
        self.add_option_menu(gui)
        self.add_note(gui)
        self.add_end_tr_button(gui)

        # self.tunner.gui.items[name] = {}
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

    def add_option_menu(self, gui):
        gui["option"] = LabeledOptionMenu.build(gui["frame"], self.gcfg["dialog"]["option"])
        gui["option"].option_variable.set(self.tunner.data["end.status"])
        gui["option"].option_variable.trace("w", self.tunner.handler.build(Message.update_end_status, gui["option"]))

    def add_note(self, gui):
        gui["note"] = Note.build(gui["frame"], self.gcfg["dialog"]["note"])
        gui["note"].text.insert(1.0, self.note_text())
        gui["note"].text.bind("<FocusOut>", self.tunner.handler.build(Message.update_end_status_note, gui["note"]))
        gui["note"].text.bind("<Key>", self.tunner.handler.build(Message.update_end_status_note, gui["note"]))

    def add_end_tr_button(self, gui):
        gui["end_tr_button"] = tk.Button(gui["frame"])
        gui["end_tr_button"].configure(**self.gcfg["dialog"]["button_end_test_run"]["configure"])
        gui["end_tr_button"].grid(**self.gcfg["dialog"]["button_end_test_run"]["grid"])
        gui["end_tr_button"].bind("<Button-1>", self.tunner.handler.build(Message.end_test))

    def note_text(self):
        return "\n".join(self.tunner.data["end.status.note"])


class NoteUpdater(TunnerSubscriber):
    subscription_messages = [Message.update_end_status_note]

    def update(self, notification):
        self.tunner.data["end.status.note"] = notification.publisher.text.get(1.0, tk.END).split("\n")


class StatusUpdater(TunnerSubscriber):
    subscription_messages = [Message.update_end_status]

    def update(self, notification):
        self.tunner.data["end.status"] = notification.publisher.option_variable.get()


class EndDataWriter(TunnerSubscriber):
    subscription_messages = [Message.write_end_data]

    def update(self, notification):
        content = {
            "end.status": self.tunner.data["end.status"],
            "end.status.note": self.tunner.data["end.status.note"]
        }
        self.tunner.auto_configuration.write_previous_cfg(content, __file__)


class EndPanelButtonEnabler(TunnerSubscriber):
    subscription_messages = [Message.run_test]

    def update(self, notification):
        self.tunner.data["_end.button.state"] = tk.NORMAL
        self.tunner.gui.items[name]["button"]["state"] = tk.NORMAL
        self.tunner.gui.items[name]["button"].bind("<Button-1>", self.tunner.handler.build(Message.switch_end_window))


class EndPanelButtonDisabler(TunnerSubscriber):
    subscription_messages = [Message.end_test]

    def update(self, notification):
        self.tunner.data["_end.button.state"] = tk.DISABLED
        self.tunner.gui.items[name]["button"]["state"] = tk.DISABLED
        self.tunner.gui.items[name]["button"].bind("<Button-1>", self.tunner.handler.build(Message.unsubscribed_message))


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
        gui["button"]["state"] = self.tunner.data["_end.button.state"]
        gui["button"].grid(**self.gcfg["plugin"]["button"]["grid"])

        if self.tunner.data["_end.button.state"] == tk.NORMAL:
            gui["button"].bind("<Button-1>", self.tunner.handler.build(Message.switch_end_window))
        else:
            gui["button"].bind("<Button-1>", self.tunner.handler.build(Message.unsubscribed_message))


class EndPlugin(yapsy.IPlugin.IPlugin):
    def __init__(self):
        super().__init__()
        self.tunner = None
        self.subscribers_classes = [
            GuiConfigurationLoader,
            PreviousConfigurationLoader,
            PanelAdder,
            EndWindowOpener,
            EndWindowCloser,
            EndWindowSwitcher,
            NoteUpdater,
            StatusUpdater,
            EndDataWriter,
            EndPanelButtonEnabler,
            EndPanelButtonDisabler,
            TunnerFileWriter,
            TestRunEnder
        ]

        self.subscribers = []

    def initialize(self, tunner):
        self.tunner = tunner

        for cls in self.subscribers_classes:
            self.subscribers.append(cls(self.tunner))

        self.tunner.data["_end.button.state"] = tk.DISABLED