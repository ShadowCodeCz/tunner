try:
    import Tkinter as tk
except Exception as e:
    import tkinter as tk


from . import starter_widgets


class WidgetType:
    labeled_entry = "labeled_entry"
    working_directory = "working_directory"
    variable = "variable"
    note = "note"
    button = "button"


class Gui(object):
    def __init__(self):
        self.root = None
        self.working_directory = None
        self.variables = []
        self.tags = None
        self.note = None
        self.button = None


class GuiBuilder:
    def __init__(self):
        self.root = None
        self.configurations = None
        self.sub_builders = {
            WidgetType.labeled_entry: LabeledEntry.build,
            WidgetType.working_directory: WorkingDirectory.build,
            WidgetType.variable: Variable.build,
            WidgetType.note: Note.build,
            WidgetType.button: Button.build
        }

    def build(self, root, configurations):
        self.root = root
        self.configurations = configurations

        gui = Gui()

        for configuration in configurations:
            builder = self.sub_builders[configuration["widget_type"]]
            widget = builder(root, configuration)
            if "variable" in configuration["name"]:
                gui.variables.append(widget)
            else:
                gui.__dict__[configuration["name"]] = widget

        return gui


class LabeledEntry(object):
    def __init__(self, *args, **kwargs):
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

        obj.entry_string = tk.StringVar()
        obj.entry = tk.Entry(obj.frame, textvariable=obj.entry_string)
        obj.entry.grid(**cfg["entry"]["grid"])
        obj.entry.configure(**cfg["entry"]["configure"])

        obj.frame.grid(**cfg["grid"])
        obj.frame.configure(**cfg["configure"])
        return obj


class WorkingDirectory(object):
    def __init__(self, *args, **kwargs):
        self.frame = None
        self.label = None
        self.label_string = None
        self.entry = None
        self.entry_string = None
        self.dialog_button = None

    @classmethod
    def build(cls, root, cfg):
        obj = cls()

        obj.frame = tk.Frame(root)
        obj.label_string = tk.StringVar()
        obj.label_string.set(cfg["label"]["text"])
        obj.label = tk.Label(obj.frame, textvariable=obj.label_string)
        obj.label.grid(**cfg["label"]["grid"])
        obj.label.configure(**cfg["label"]["configure"])

        obj.entry_string = tk.StringVar()
        obj.entry = tk.Entry(obj.frame, textvariable=obj.entry_string)
        obj.entry.grid(**cfg["entry"]["grid"])
        obj.entry.configure(**cfg["entry"]["configure"])

        obj.dialog_button = tk.Button(obj.frame, text="open")
        obj.dialog_button.grid(**cfg["button"]["grid"])
        obj.dialog_button.configure(**cfg["button"]["configure"])

        obj.frame.grid(**cfg["grid"])
        obj.frame.configure(**cfg["configure"])
        return obj


class Variable(object):
    def __init__(self, *args, **kwargs):
        self.frame = None
        self.label = None
        self.label_string = None
        self.variable = None
        self.variable_string = None
        self.value = None
        self.value_string = None
        self.checkbox = None
        self.checkbox_variable = None

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

        obj.checkbox_variable = tk.IntVar()
        obj.checkbox = tk.Checkbutton(obj.frame, variable=obj.checkbox_variable)
        obj.checkbox.grid(**cfg["checkbox"]["grid"])
        obj.checkbox.configure(**cfg["checkbox"]["configure"])

        obj.frame.grid(**cfg["grid"])
        obj.frame.configure(**cfg["configure"])

        return obj


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

        return obj


class Button(object):
    def __init__(self):
        self.button = None

    @classmethod
    def build(cls, root, cfg):
        obj = cls()

        obj.button = tk.Button(root)

        obj.button.grid(**cfg["grid"])
        obj.button.configure(**cfg["configure"])

        return obj


def build(root):
    # root = tk.Tk()

    builder = GuiBuilder()
    gui = builder.build(root, starter_widgets.configurations)

    root.configure(bg="#434343")
    root.title("TUNNER: Starter")

    return gui
    # root.mainloop()
