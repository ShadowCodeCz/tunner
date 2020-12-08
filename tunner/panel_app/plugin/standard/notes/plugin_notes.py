import os
import datetime
import copy
import generic_design_patterns as gdp
import yapsy.IPlugin

try:
    import Tkinter as tk
except Exception as e:
    import tkinter as tk


name = "plugin.notes"


class Message:
    load_plugin_gui_configuration = "load.plugin.gui.configuration"
    load_plugin_previous_configuration = "load.plugin.previous.configuration"

    add_plugin_to_panel = "add.plugin.to.panel"
    close_plugin_start_window = "close.plugin.notes.window"
    open_plugin_notes_window = "open.plugin.notes.window"
    switch_notes_window = "switch.notes.window"
    close_plugins_windows = "close.plugins.windows"

    update_tr_note = "update.tr.note"
    update_tp_note = "update.tp.note"

    write_notes = "write.notes"

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

        obj.frame.columnconfigure(0, weight=1)
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


class NotesWindowSwitcher(TunnerSubscriber):
    subscription_messages = [Message.switch_notes_window]
    # visible = False

    def update(self, notification):
        if self.is_open():
            self.send_close_notification()
            # self.visible = False
        else:
            self.send_open_notification()
            # self.visible = True

    def send_open_notification(self):
        notification = gdp.event.Notification(Message.open_plugin_notes_window, self)
        self.tunner.provider.notify(notification)

    def send_close_notification(self):
        notification = gdp.event.Notification(Message.close_plugin_start_window, self)
        self.tunner.provider.notify(notification)

    def is_open(self):
        try:
            return self.tunner.gui.items[name]["dialog"] != {}
        except:
            return False


class AbstractNoteUpdater(TunnerSubscriber):
    subscription_messages = []
    key = ""

    def update(self, notification):
        self.tunner.data[self.key] = notification.publisher.text.get(1.0, tk.END).split("\n")


class TrNoteUpdater(AbstractNoteUpdater):
    subscription_messages = [Message.update_tr_note]
    key = "tr.note"


class TpNoteUpdater(AbstractNoteUpdater):
    subscription_messages = [Message.update_tp_note]
    key = "tp.note"


class NotesWriter(TunnerSubscriber):
    subscription_messages = [Message.write_notes]

    def update(self, notification):
        content = {
            "tr.note": self.tunner.data["tr.note"],
            "tp.note": self.tunner.data["tp.note"]
        }
        self.tunner.auto_configuration.write_previous_cfg(content, __file__)


class NotesWindowCloser(TunnerSubscriber):
    subscription_messages = [Message.close_plugin_start_window, Message.close_plugins_windows]

    def update(self, notification):
        if "dialog" in self.tunner.gui.items[name] and self.tunner.gui.items[name]["dialog"] != {}:
            self.write_window_data_to_file()
            self.tunner.gui.items[name]["dialog"]["frame"].destroy()
            self.tunner.gui.items[name]["dialog"] = {}

    def write_window_data_to_file(self):
        notification = gdp.event.Notification(Message.write_notes)
        self.tunner.provider.notify(notification)


class NotesWindowOpener(TunnerSubscriber):
    subscription_messages = [Message.open_plugin_notes_window]

    def update(self, notification):
        gui = {}

        self.create_frame(gui)
        self.set_top_panel(gui)
        self.add_notes_widgets(gui)
        self.configure_columns(gui)

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
            gui["frame"].minsize(self.tunner.gui.root.winfo_screenwidth(), self.tunner.gui.root.winfo_reqheight())

    def add_notes_widgets(self, gui):
        self.add_note_widget(gui, "tr.note", "Test Run Note", 0, 0, Message.update_tr_note)
        self.add_note_widget(gui, "tp.note", "Test Procedure Note", 0, 1, Message.update_tp_note)

    def configure_columns(self, gui):
        gui["frame"].columnconfigure(0, weight=1)
        gui["frame"].columnconfigure(1, weight=1)

    def add_note_widget(self, gui, key, label_text, row, column, message):
        cfg = copy.deepcopy(self.gcfg["dialog"]["note"])
        cfg["label"]["text"] = label_text
        cfg["grid"]["row"] = row
        cfg["grid"]["column"] = column

        note = Note.build(gui["frame"], cfg)
        note.text.insert(1.0, "\n".join(self.tunner.data[key]))
        note.text.bind("<FocusOut>", self.tunner.handler.build(message, note))
        note.text.bind("<Key>", self.tunner.handler.build(message, note))

        gui[key] = note


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
        gui["button"].bind("<Button-1>", self.tunner.handler.build(Message.switch_notes_window))


class NotesPlugin(yapsy.IPlugin.IPlugin):
    def __init__(self):
        super().__init__()
        self.tunner = None
        self.subscribers_classes = [
            GuiConfigurationLoader,
            PreviousConfigurationLoader,
            PanelAdder,
            NotesWindowOpener,
            NotesWindowCloser,
            NotesWindowSwitcher,
            TrNoteUpdater,
            TpNoteUpdater,
            NotesWriter
        ]

        self.subscribers = []

    def initialize(self, tunner):
        self.tunner = tunner

        for cls in self.subscribers_classes:
            self.subscribers.append(cls(self.tunner))