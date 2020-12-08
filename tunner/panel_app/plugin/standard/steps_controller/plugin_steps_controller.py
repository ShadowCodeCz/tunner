import generic_design_patterns as gdp
import yapsy.IPlugin

try:
    import Tkinter as tk
except Exception as e:
    import tkinter as tk


name = "plugin.steps.controller"


class Message:
    load_plugin_gui_configuration = "load.plugin.gui.configuration"
    load_plugin_previous_configuration = "load.plugin.previous.configuration"

    add_plugin_to_panel = "add.plugin.to.panel"
    close_plugin_steps_controller_window = "close.plugin.steps.controller.window"
    open_plugin_steps_controller_window = "open.plugin.steps.controller.window"
    switch_steps_controller_window = "switch.steps.controller.window"
    close_plugins_windows = "close.plugins.windows"

    previous_test_step = "previous.test.step"
    next_test_step = "next.test.step"
    test_step_update = "test.step.update"
    test_available = "test.available"

    add_step_comment = "add.step.comment"

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

    @property
    def gui_items(self):
        return self.tunner.gui.items[name]


class GuiConfigurationLoader(TunnerSubscriber):
    subscription_messages = [Message.load_plugin_gui_configuration]

    def update(self, notification):
        self.tunner.gui.cfg[name] = self.tunner.auto_configuration.load_gui_cfg(__file__)


class StepsWindowSwitcher(TunnerSubscriber):
    subscription_messages = [Message.switch_steps_controller_window]

    def update(self, notification):
        if self.is_open():
            self.send_close_notification()
        else:
            self.send_open_notification()

    def send_open_notification(self):
        notification = gdp.event.Notification(Message.open_plugin_steps_controller_window, self)
        self.tunner.provider.notify(notification)

    def send_close_notification(self):
        notification = gdp.event.Notification(Message.close_plugin_steps_controller_window, self)
        self.tunner.provider.notify(notification)

    def is_open(self):
        try:
            return self.tunner.gui.items[name]["dialog"] != {}
        except:
            return False


class StepsWindowCloser(TunnerSubscriber):
    subscription_messages = [Message.close_plugin_steps_controller_window, Message.close_plugins_windows]

    def update(self, notification):
        if "dialog" in self.tunner.gui.items[name] and self.tunner.gui.items[name]["dialog"] != {}:
            # self.write_window_data_to_file()
            self.tunner.gui.items[name]["dialog"]["frame"].destroy()
            self.tunner.gui.items[name]["dialog"] = {}


class CommentAdder(TunnerSubscriber):
    subscription_messages = [Message.add_step_comment]

    def update(self, notification):

        comment = {
            "step": self.tunner.data["step"],
            "type": self.gui_items["dialog"]["type_option"].option_variable.get(),
            "column": self.gui_items["dialog"]["column_option"].option_variable.get(),
            "text": self.gui_items["dialog"]["note"].text.get(1.0, tk.END).split("\n")
        }

        self.tunner.data["comments"].append(comment)


class StepsWindowOpener(TunnerSubscriber):
    subscription_messages = [Message.open_plugin_steps_controller_window]

    def update(self, notification):
        gui = {}

        self.create_frame(gui)
        self.set_top_panel(gui)
        # self.build_gui(gui)
        self.add_type_option_menu(gui)
        self.add_column_option_menu(gui)
        self.add_note(gui)
        self.add_comment_button(gui)

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

    def add_type_option_menu(self, gui):
        gui["type_option"] = LabeledOptionMenu.build(gui["frame"], self.gcfg["dialog"]["type_option"])
        # gui["option"].option_variable.set(self.tunner.data["end.status"])
        gui["type_option"].option_variable.trace("w", self.tunner.handler.build(Message.unsubscribed_message, gui["type_option"]))

    def add_column_option_menu(self, gui):
        self.gcfg["dialog"]["column_option"]["option_menu"]["options_list"] += self.tunner.data["test"]["header"]
        gui["column_option"] = LabeledOptionMenu.build(gui["frame"], self.gcfg["dialog"]["column_option"])
        # gui["option"].option_variable.set(self.tunner.data["end.status"])
        gui["column_option"].option_variable.trace("w", self.tunner.handler.build(Message.unsubscribed_message, gui["column_option"]))

        # gui["column_option"].option_variable.set(cfg["option_menu"]["options_list"][0])

    def add_note(self, gui):
        gui["note"] = Note.build(gui["frame"], self.gcfg["dialog"]["note"])
        # gui["note"].text.insert(1.0, self.note_text())
        gui["note"].text.bind("<FocusOut>", self.tunner.handler.build(Message.unsubscribed_message, gui["note"]))
        gui["note"].text.bind("<Key>", self.tunner.handler.build(Message.unsubscribed_message, gui["note"]))

    def add_comment_button(self, gui):
        # TODO: unify naming of buttons, widgets ...
        gui["comment_button"] = tk.Button(gui["frame"])
        gui["comment_button"].configure(**self.gcfg["dialog"]["button_comment"]["configure"])
        gui["comment_button"].grid(**self.gcfg["dialog"]["button_comment"]["grid"])
        gui["comment_button"].bind("<Button-1>", self.tunner.handler.build(Message.add_step_comment))

    def note_text(self):
        return "\n".join(self.tunner.data["end.status.note"])


class StepsControllerEnabler(TunnerSubscriber):
    subscription_messages = [Message.test_available]

    def update(self, notification):
        self.tunner.data["_previous.step.button.state"] = tk.NORMAL
        self.gui_items["previous_button"]["state"] = self.tunner.data["_previous.step.button.state"]
        self.gui_items["previous_button"].bind("<Button-1>", self.tunner.handler.build(Message.previous_test_step))

        self.tunner.data["_next.step.button.state"] = tk.NORMAL
        self.gui_items["next_button"]["state"] = self.tunner.data["_next.step.button.state"]
        self.gui_items["next_button"].bind("<Button-1>", self.tunner.handler.build(Message.next_test_step))

        self.tunner.data["_step.button.state"] = tk.NORMAL
        self.gui_items["step_number_button"]["state"] = self.tunner.data["_step.button.state"]
        self.gui_items["step_number_button"].bind("<Button-1>", self.tunner.handler.build(Message.switch_steps_controller_window))

        notification = gdp.event.Notification(Message.test_step_update)
        self.tunner.provider.notify(notification)

# class StepsControllerDisabler(TunnerSubscriber):
#     subscription_messages = [Message.disable_widget]
#
#     def update(self, notification):


class MoveButtonStateController(TunnerSubscriber):
    subscription_messages = [Message.test_step_update]
    button = ""
    enable_message = ""
    disable_message = Message.unsubscribed_message

    def update(self, notification):
        if self.enable_for_current_step():
            self.enable()
        else:
            self.disable()

    def enable_for_current_step(self):
        pass

    def enable(self):
        # condition = name in self.tunner.gui.items
        #
        # if condition:
        self.tunner.gui.items[name][self.button]["state"] = tk.NORMAL
        self.tunner.gui.items[name][self.button].bind("<Button-1>", self.tunner.handler.build(self.enable_message))

    def disable(self):
        # condition = name in self.tunner.gui.items
        # if condition:
        self.tunner.gui.items[name][self.button]["state"] = tk.DISABLED
        self.tunner.gui.items[name][self.button].bind("<Button-1>", self.tunner.handler.build(self.disable_message))


class PreviousButtonStateController(MoveButtonStateController):
    button = "previous_button"
    enable_message = Message.previous_test_step

    def enable_for_current_step(self):
        return self.tunner.data["step"] > 0


class NextButtonStateController(MoveButtonStateController):
    button = "next_button"
    enable_message = Message.next_test_step

    def enable_for_current_step(self):
        return self.tunner.data["step"] < len(self.tunner.data["test"]["steps"]) - 1


class StepIDUpdater(TunnerSubscriber):
    subscription_messages = [Message.test_step_update]

    def update(self, notification):
        # condition = name in self.tunner.gui.items
        # if self.tunner.data["step"] != -1:
        step = self.tunner.data["step"]
        step_number = self.tunner.data["test"]["steps"][step][0]["original.text"]
        self.gui_items["step_number_button"].configure(text=step_number)


class PreviousStepUpdater(TunnerSubscriber):
    subscription_messages = [Message.previous_test_step]

    def update(self, notification):
        self.tunner.data["step"] -= 1

        notification = gdp.event.Notification(Message.test_step_update)
        self.tunner.provider.notify(notification)


class NextStepUpdater(TunnerSubscriber):
    subscription_messages = [Message.next_test_step]

    def update(self, notification):
        self.tunner.data["step"] += 1

        notification = gdp.event.Notification(Message.test_step_update)
        self.tunner.provider.notify(notification)


class PanelAdder(TunnerSubscriber):
    subscription_messages = [Message.add_plugin_to_panel]

    def update(self, notification):
        gui = {}

        self.add_frame(gui)
        self.add_previous_button(gui)
        self.add_next_button(gui)
        self.add_step_number_button(gui)

        self.tunner.gui.items[name] = gui

        if self.tunner.data["step"] != -1:
            notification = gdp.event.Notification(Message.test_step_update)
            self.tunner.provider.notify(notification)

    def add_frame(self, gui):
        gui["frame"] = tk.Frame(self.tunner.gui.panel["frame"])
        gui["frame"].configure(**self.gcfg["plugin"]["frame"]["configure"])
        gui["frame"].grid(**self.gcfg["plugin"]["frame"]["grid"])

    def add_previous_button(self, gui):
        gui["previous_button"] = tk.Button(gui["frame"])
        gui["previous_button"].configure(**self.gcfg["plugin"]["previous_button"]["configure"])
        gui["previous_button"]["state"] = self.tunner.data["_previous.step.button.state"]
        gui["previous_button"].grid(**self.gcfg["plugin"]["previous_button"]["grid"])
        message = Message.previous_test_step if self.tunner.data["_previous.step.button.state"] == tk.NORMAL else Message.unsubscribed_message
        gui["previous_button"].bind("<Button-1>", self.tunner.handler.build(message))

    def add_next_button(self, gui):
        gui["next_button"] = tk.Button(gui["frame"])
        gui["next_button"].configure(**self.gcfg["plugin"]["next_button"]["configure"])
        gui["next_button"]["state"] = self.tunner.data["_next.step.button.state"]
        gui["next_button"].grid(**self.gcfg["plugin"]["next_button"]["grid"])
        message = Message.next_test_step if self.tunner.data["_next.step.button.state"] == tk.NORMAL else Message.unsubscribed_message
        gui["next_button"].bind("<Button-1>", self.tunner.handler.build(message))

    def add_step_number_button(self, gui):
        gui["step_number_button"] = tk.Button(gui["frame"])
        gui["step_number_button"].configure(**self.gcfg["plugin"]["step_number_button"]["configure"])
        gui["step_number_button"]["state"] = self.tunner.data["_step.button.state"]
        gui["step_number_button"].grid(**self.gcfg["plugin"]["step_number_button"]["grid"])
        message = Message.switch_steps_controller_window if self.tunner.data["_step.button.state"] == tk.NORMAL else Message.unsubscribed_message
        gui["step_number_button"].bind("<Button-1>", self.tunner.handler.build(message))


class StepsControllerPlugin(yapsy.IPlugin.IPlugin):
    def __init__(self):
        super().__init__()
        self.tunner = None
        self.subscribers_classes = [
            GuiConfigurationLoader,
            PanelAdder,
            StepIDUpdater,
            NextButtonStateController,
            PreviousButtonStateController,
            NextStepUpdater,
            PreviousStepUpdater,
            StepsControllerEnabler,
            StepsWindowCloser,
            StepsWindowOpener,
            StepsWindowSwitcher,
            CommentAdder
        ]

        self.subscribers = []

    def initialize(self, tunner):
        self.tunner = tunner

        for cls in self.subscribers_classes:
            self.subscribers.append(cls(self.tunner))

        self.tunner.data["_previous.step.button.state"] = tk.DISABLED
        self.tunner.data["_next.step.button.state"] = tk.DISABLED
        self.tunner.data["_step.button.state"] = tk.DISABLED

        self.tunner.data["comments"] = []