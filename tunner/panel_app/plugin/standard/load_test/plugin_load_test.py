import os
import datetime
import json
import generic_design_patterns as gdp
import yapsy.IPlugin

try:
    import Tkinter as tk
except Exception as e:
    import tkinter as tk

name = "plugin.load.test"


class Message:
    load_plugin_gui_configuration = "load.plugin.gui.configuration"
    add_plugin_to_panel = "add.plugin.to.panel"
    close_plugin_load_test_window = "close.plugin.load.test.window"
    open_plugin_load_test_window = "open.plugin.load.test.window"
    load_plugin_previous_configuration = "load.plugin.previous.configuration"
    switch_load_test_window = "switch.load.test.window"
    close_plugins_windows = "close.plugins.windows"
    update_test_file_path = "update.test.file.path"
    write_test_file_path = "write.test.file.path"
    run_test = "run.test"
    end_test = "end.test"
    load_test_file = "load.test.file"
    create_table_empty_test = "create.empty.table.test"
    create_simple_empty_test = "create.empty.simple.test"
    unsubscribed_message = "unsubscribed.message"
    test_available = "test.available"
    test_step_update = "test.step.update"


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


class LoadTestWindowSwitcher(TunnerSubscriber):
    subscription_messages = [Message.switch_load_test_window]

    # visible = False

    def update(self, notification):
        if self.is_open():
            self.send_close_notification()
            # self.visible = False
        else:
            self.send_open_notification()
            # self.visible = True

    def send_open_notification(self):
        notification = gdp.event.Notification(Message.open_plugin_load_test_window, self)
        self.tunner.provider.notify(notification)

    def send_close_notification(self):
        notification = gdp.event.Notification(Message.close_plugin_load_test_window, self)
        self.tunner.provider.notify(notification)

    def is_open(self):
        try:
            return self.tunner.gui.items[name]["dialog"] != {}
        except:
            return False


class LoadTestWindowCloser(TunnerSubscriber):
    subscription_messages = [Message.close_plugin_load_test_window, Message.close_plugins_windows]

    def update(self, notification):
        condition = name in self.tunner.gui.items and \
                    "dialog" in self.tunner.gui.items[name] and\
                    self.tunner.gui.items[name]["dialog"] != {}
        if condition:
            self.write_window_data_to_file()
            self.tunner.gui.items[name]["dialog"]["frame"].destroy()
            self.tunner.gui.items[name]["dialog"] = {}

    def write_window_data_to_file(self):
        notification = gdp.event.Notification(Message.write_test_file_path, self)
        self.tunner.provider.notify(notification)


class TestStepsGetter(TunnerSubscriber):
    def send_notifications(self):
        self.send_notification_close_window()
        self.send_notification_test_step_update()
        self.send_notification_test_steps_available()

    def send_notification_test_steps_available(self):
        notification = gdp.event.Notification(Message.test_available)
        self.tunner.provider.notify(notification)

    def send_notification_test_step_update(self):
        notification = gdp.event.Notification(Message.test_step_update)
        self.tunner.provider.notify(notification)

    def send_notification_close_window(self):
        notification = gdp.event.Notification(Message.close_plugin_load_test_window)
        self.tunner.provider.notify(notification)

    def update_variables(self):
        # TODO: It will not save to previous.json (variable.plugin) without opening window
        self.tunner.variables.set("test.id", self.tunner.data["test"]["id"])
        self.tunner.variables.set("test.title", self.tunner.data["test"]["title"])


class TestFileLoader(TestStepsGetter):
    subscription_messages = [Message.load_test_file]

    def update(self, notification):
        with open(self.tunner.data["test.file.path"]) as f:
            self.tunner.data["test"] = json.load(f)

        self.tunner.data["step"] = 0

        self.update_variables()
        self.send_notifications()



class EmptyTableTestCreator(TestStepsGetter):
    subscription_messages = [Message.create_table_empty_test]

    def update(self, notification):
        empty = {
            "title": "",
            "id": "",
            "header": ["id", "short", "action", "expected"],
            "steps": [[{"original.text": str(i)}, {"original.text": ""}, {"original.text": ""}, {"original.text": ""}] for i in range(1, 55)]
        }

        self.tunner.data["test"] = empty
        self.tunner.data["step"] = 0

        self.update_variables()
        self.send_notifications()



class EmptySimpleTestCreator(TestStepsGetter):
    subscription_messages = [Message.create_simple_empty_test]

    def update(self, notification):
        empty = {
            "title": "",
            "id": "",
            "header": ["id", "short", "action"],
            "steps": [[{"original.text": str(i)}, {"original.text": ""}, {"original.text": ""}] for i in range(1, 55)]
        }

        self.tunner.data["test"] = empty
        self.tunner.data["step"] = 0

        self.update_variables()
        self.send_notifications()



class TestFilePathTemplateWriter(TunnerSubscriber):
    subscription_messages = [Message.write_test_file_path]

    def update(self, notification):
        # TODO: second option use self.tunner.data
        content = {
            "test.file.path": self.tunner.gui.items[name]["dialog"]["path_entry"].entry_string.get()
        }
        self.tunner.auto_configuration.write_previous_cfg(content, __file__)


class TestFilePathTemplateUpdater(TunnerSubscriber):
    subscription_messages = [Message.update_test_file_path]

    def update(self, notification):
        self.tunner.data["test.file.path"] = notification.publisher.entry.get()


class LoadTestWindowOpener(TunnerSubscriber):
    subscription_messages = [Message.open_plugin_load_test_window]

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
        self.add_load_test_button(gui)
        self.add_create_empty_simple_test_button(gui)
        self.add_create_empty_table_test_button(gui)

    def add_directory_entry(self, gui):
        gui["path_entry"] = LabeledEntry.build(gui["frame"], self.gcfg["dialog"]["path_entry"])
        gui["path_entry"].entry_string.set(self.tunner.data["test.file.path"])
        gui["path_entry"].entry_string.trace("w", self.tunner.handler.build(Message.update_test_file_path,
                                                                            gui["path_entry"]))

    def add_load_test_button(self, gui):
        gui["load_test_button"] = tk.Button(gui["frame"])
        gui["load_test_button"].configure(**self.gcfg["dialog"]["button_load_test"]["configure"])
        gui["load_test_button"].grid(**self.gcfg["dialog"]["button_load_test"]["grid"])
        gui["load_test_button"].bind("<Button-1>", self.tunner.handler.build(Message.load_test_file, gui["path_entry"]))

    def add_create_empty_simple_test_button(self, gui):
        gui["create_empty_simple_test_button"] = tk.Button(gui["frame"])
        gui["create_empty_simple_test_button"].configure(**self.gcfg["dialog"]["button_create_simple_empty_test"]["configure"])
        gui["create_empty_simple_test_button"].grid(**self.gcfg["dialog"]["button_create_simple_empty_test"]["grid"])
        gui["create_empty_simple_test_button"].bind("<Button-1>", self.tunner.handler.build(Message.create_simple_empty_test))

    def add_create_empty_table_test_button(self, gui):
        gui["create_empty_table_test_button"] = tk.Button(gui["frame"])
        gui["create_empty_table_test_button"].configure(**self.gcfg["dialog"]["button_create_table_empty_test"]["configure"])
        gui["create_empty_table_test_button"].grid(**self.gcfg["dialog"]["button_create_table_empty_test"]["grid"])
        gui["create_empty_table_test_button"].bind("<Button-1>", self.tunner.handler.build(Message.create_table_empty_test))


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
        # gui["button"]["state"] = self.tunner.data["_load_steps.button.state"]
        gui["button"].grid(**self.gcfg["plugin"]["button"]["grid"])
        gui["button"].bind("<Button-1>", self.tunner.handler.build(Message.switch_load_test_window))

        # if self.tunner.data["_load_steps.button.state"] == tk.NORMAL:
        #     gui["button"].bind("<Button-1>", self.tunner.handler.build(Message.switch_load_test_window))
        # else:
        #     gui["button"].bind("<Button-1>", self.tunner.handler.build(Message.unsubscribed_message))


# class LoadTestPanelButtonEnabler(TunnerSubscriber):
#     subscription_messages = [Message.end_test]
#
#     def update(self, notification):
#         self.tunner.data["_load_steps.button.state"] = tk.NORMAL
#         self.tunner.gui.items[name]["button"]["state"] = tk.NORMAL
#         self.tunner.gui.items[name]["button"].bind("<Button-1>",
#                                                    self.tunner.handler.build(Message.switch_load_test_window))


# class LoadTestPanelButtonDisabler(TunnerSubscriber):
#     subscription_messages = [Message.run_test]
#
#     def update(self, notification):
#         self.tunner.data["_load_steps.button.state"] = tk.DISABLED
#         self.tunner.gui.items[name]["button"]["state"] = tk.DISABLED
#         self.tunner.gui.items[name]["button"].bind("<Button-1>",
#                                                    self.tunner.handler.build(Message.unsubscribed_message))


class LoadTestPlugin(yapsy.IPlugin.IPlugin):
    def __init__(self):
        super().__init__()
        self.tunner = None
        self.subscribers_classes = [
            GuiConfigurationLoader,
            PreviousConfigurationLoader,
            PanelAdder,
            LoadTestWindowOpener,
            LoadTestWindowCloser,
            LoadTestWindowSwitcher,
            TestFileLoader,
            TestFilePathTemplateUpdater,
            TestFilePathTemplateWriter,
            # LoadTestPanelButtonEnabler,
            # LoadTestPanelButtonDisabler,
            EmptyTableTestCreator,
            EmptySimpleTestCreator
        ]

        self.subscribers = []

    def initialize(self, tunner):
        self.tunner = tunner

        for cls in self.subscribers_classes:
            self.subscribers.append(cls(self.tunner))

        self.tunner.data["step"] = -1
        self.tunner.data["test"] = {}
        # self.tunner.data["_load_steps.button.state"] = tk.NORMAL
        # Message.create_simple_empty_test
