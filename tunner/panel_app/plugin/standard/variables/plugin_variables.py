import os
import datetime
import copy
import generic_design_patterns as gdp
import yapsy.IPlugin

try:
    import Tkinter as tk
except Exception as e:
    import tkinter as tk


name = "plugin.variables"


class Message:
    load_plugin_gui_configuration = "load.plugin.gui.configuration"
    load_plugin_previous_configuration = "load.plugin.previous.configuration"

    add_plugin_to_panel = "add.plugin.to.panel"
    close_plugin_start_window = "close.plugin.variables.window"
    open_plugin_variables_window = "open.plugin.variables.window"
    switch_variables_window = "switch.variables.window"
    close_plugins_windows = "close.plugins.windows"

    update_variable_name = "update.variable.name"
    update_variable_value = "update.variable.value"

    #TODO: Dirty solution
    test_id_updated = "test.id.updated"

    write_variables = "write.variables"

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


class Variable(object):
    def __init__(self, *args, **kwargs):
        self.frame = None
        self.label = None
        self.label_string = None
        # TODO: change "variable_name"
        self.variable = None
        self.variable_string = None
        self.value = None
        self.value_string = None
        self.index = None

    @classmethod
    def build(cls, root, cfg):
        obj = cls()

        obj.frame = tk.Frame(root)

        obj.label_string = tk.StringVar()
        obj.label_string.set(cfg["label"]["text"])
        obj.label = tk.Label(obj.frame, textvariable=obj.label_string)
        obj.label.grid(**cfg["label"]["grid"])
        obj.label.configure(**cfg["label"]["configure"])

        obj.variable_string = tk.StringVar()
        obj.variable = tk.Entry(obj.frame, textvariable=obj.variable_string)
        obj.variable.grid(**cfg["variable"]["grid"])
        obj.variable.configure(**cfg["variable"]["configure"])

        obj.value_string = tk.StringVar()
        obj.value = tk.Entry(obj.frame, textvariable=obj.value_string)
        obj.value.grid(**cfg["value"]["grid"])
        obj.value.configure(**cfg["value"]["configure"])

        obj.frame.grid(**cfg["grid"])
        obj.frame.configure(**cfg["configure"])

        obj.frame.columnconfigure(1, weight=1)
        obj.frame.columnconfigure(2, weight=3)

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


class VariablesWindowSwitcher(TunnerSubscriber):
    subscription_messages = [Message.switch_variables_window]
    # visible = False

    def update(self, notification):
        if self.is_open():
            self.send_close_notification()
            # self.visible = False
        else:
            self.send_open_notification()
            # self.visible = True

    def send_open_notification(self):
        notification = gdp.event.Notification(Message.open_plugin_variables_window, self)
        self.tunner.provider.notify(notification)

    def send_close_notification(self):
        notification = gdp.event.Notification(Message.close_plugin_start_window, self)
        self.tunner.provider.notify(notification)

    def is_open(self):
        try:
            return self.tunner.gui.items[name]["dialog"] != {}
        except:
            return False


class VariablesWindowCloser(TunnerSubscriber):
    subscription_messages = [Message.close_plugin_start_window, Message.close_plugins_windows]

    def update(self, notification):
        if "dialog" in self.tunner.gui.items[name] and self.tunner.gui.items[name]["dialog"] != {}:
            self.write_window_data_to_file()
            self.tunner.gui.items[name]["dialog"]["frame"].destroy()
            self.tunner.gui.items[name]["dialog"] = {}

    def write_window_data_to_file(self):
        notification = gdp.event.Notification(Message.write_variables, self)
        self.tunner.provider.notify(notification)


class VariablesWriter(TunnerSubscriber):
    subscription_messages = [Message.write_variables]

    def update(self, notification):
        content = {
            "variables": self.tunner.data["variables"]
        }
        self.tunner.auto_configuration.write_previous_cfg(content, __file__)


class VariablesWindowOpener(TunnerSubscriber):
    subscription_messages = [Message.open_plugin_variables_window]

    def update(self, notification):
        gui = {}

        self.create_frame(gui)
        self.set_top_panel(gui)
        self.build_variables_gui(gui)

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

    def build_variables_gui(self, gui):
        gui["variables"] = []

        for i in range(0, len(self.tunner.data["variables"])):
            self.build_variable_gui(i, gui)

    def build_variable_gui(self, i, gui):
        cfg = self.variable_cfg(i)

        v = Variable.build(gui["frame"], cfg)
        self.set_variable_data(i, v)
        self.bind_variable(v)

        gui["variables"].append(v)

    def bind_variable(self, v):
        v.variable_string.trace("w", self.tunner.handler.build(Message.update_variable_name, v))
        v.value_string.trace("w", self.tunner.handler.build(Message.update_variable_value, v))

    def variable_cfg(self, i):
        cfg = copy.deepcopy(self.gcfg["dialog"]["variable"])
        cfg["grid"]["row"] = i
        cfg["label"]["text"] = "Variable #%s%s" % ((2 - len(str(i))) * "0", i)

        return cfg

    def set_variable_data(self, i, v):
        v.index = i
        v.variable_string.set(self.tunner.data["variables"][i]["name"])
        v.value_string.set(self.tunner.data["variables"][i]["value"])


class VariableNameUpdater(TunnerSubscriber):
    subscription_messages = [Message.update_variable_name]

    def update(self, notification):
        i = notification.publisher.index
        name = notification.publisher.variable_string.get()
        self.tunner.data["variables"][i]["name"] = name


class VariableValueUpdater(TunnerSubscriber):
    subscription_messages = [Message.update_variable_value]

    def update(self, notification):
        i = notification.publisher.index
        value = notification.publisher.value_string.get()
        self.tunner.data["variables"][i]["value"] = value

        # TODO: Rework Dirty
        if self.tunner.data["variables"][i]["name"].strip() == "test.id":
            notification = gdp.event.Notification(Message.test_id_updated)
            self.tunner.provider.notify(notification)


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
        gui["button"].bind("<Button-1>", self.tunner.handler.build(Message.switch_variables_window))


class VariablesPlugin(yapsy.IPlugin.IPlugin):
    def __init__(self):
        super().__init__()
        self.tunner = None
        self.subscribers_classes = [
            GuiConfigurationLoader,
            PreviousConfigurationLoader,
            PanelAdder,
            VariablesWindowOpener,
            VariablesWindowCloser,
            VariablesWindowSwitcher,
            VariableNameUpdater,
            VariableValueUpdater,
            VariablesWriter
        ]

        self.subscribers = []

    def initialize(self, tunner):
        self.tunner = tunner

        for cls in self.subscribers_classes:
            self.subscribers.append(cls(self.tunner))