try:
    import Tkinter as tk
except Exception as e:
    import tkinter as tk


import copy

labeled_entry = {
        "name": "",
        "widget_type": "labeled_entry",
        "grid": {"row": 0, "column": 0, "sticky": "W", "pady": (0, 4)},
        "configure": {"bg": "#434343"},
        "label": {
            "text": "",
            "grid": {"row": 0, "column": 0, "sticky": "W"},
            "configure": {
               "width": 20,
                "anchor": "w",
                "bg": "#434343",
                "fg": "#E9E9E9",
                "font": "Helvetica 9",
            }
        },
        "entry": {
            "grid": {"row": 0, "column": 1},
            "configure": {
                "width": 90,
                "highlightthickness": "2",
                "highlightbackground": "#535353",
                "relief": "flat",
                "bg": "#393939",
                "fg": "#E9E9E9",
                "font": "Helvetica 9",
                "insertbackground": "#E9E9E9"
            }
        },
    }

directory_path_entry = {
        "name": "",
        "widget_type": "working_directory",
        "grid": {"row": 0, "column": 0, "sticky": "W", "pady": (0, 4)},
        "configure": {
            "bg": "#434343"
        },
        "label": {
            "text": "",
            "grid": {"row": 0, "column": 0, "sticky": "W"},
            "configure": {
               "width": 20,
                "anchor": "w",
                "bg": "#434343",
                # "fg": "#E8CE78",
                "fg": "#E9E9E9",
                "font": "Helvetica 9",

            }
        },
        "entry": {
            "grid": {"row": 0, "column": 1, "sticky": tk.W + tk.E, "padx": (0, 6)},
            "configure": {
                "width": 85,
                "highlightthickness": "2",
                "highlightbackground": "#535353",
                "relief": "flat",
                "bg": "#393939",
                "fg": "#E9E9E9",
                "font": "Helvetica 9",
                "insertbackground": "#E9E9E9"
            }
        },
        "button": {
            "grid": {"row": 0, "column": 2, "sticky": tk.W + tk.E},
            "configure": {
                "width": 3,
                "highlightthickness": "0",
                "highlightbackground": "red",
                "relief": "flat",
                "bg": "#393939",
                "fg": "#E9E9E9",
                "font": "Helvetica 9",
                "activeforeground": "blue",
                "text": "..."
            }
        }
}

variable = {
        "name": "",
        "widget_type": "variable",
        "grid": {"row": 0, "column": 0, "stick": "W", "pady": (0, 4)},
        "configure": {"bg": "#434343"},
        "label": {
            "text": "",
            "grid": {"row": 0, "column": 0, "sticky": "W"},
            "configure": {
               "width": 20,
                "anchor": "w",
                "bg": "#434343",
                # "fg": "#E8CE78",
                "fg": "#E9E9E9",
                "font": "Helvetica 9",
            }
        },
        "variable": {
            "grid": {"row": 0, "column": 1, "padx": (0, 6)},
            "configure": {
                "width": 42,
                "highlightthickness": "2",
                "highlightbackground": "#535353",
                "relief": "flat",
                "bg": "#393939",
                "fg": "#E9E9E9",
                "font": "Helvetica 9",
                "insertbackground": "#E9E9E9"
            }
        },
        "value": {
            "grid": {"row": 0, "column": 2},
            "configure": {
                "width": 42,
                "highlightthickness": "2",
                "highlightbackground": "#535353",
                "relief": "flat",
                "bg": "#393939",
                "fg": "#E9E9E9",
                "font": "Helvetica 9",
                "insertbackground": "#E9E9E9",
            }
        },
        "checkbox": {
            "grid": {"row": 0, "column": 3},
            "configure": {
                "bg": "#434343",
                "highlightcolor": "red",
                "fg": "#E9E9E9",
                "activebackground": "#434343",
                "activeforeground": "yellow",
                "highlightbackground": "violet",
                "highlightthickness": "0",
                "selectcolor": "#434343",
                "relief": "flat"
            }
        }
}

labeled_text = {
        "name": "",
        "widget_type": "note",
        "grid": {"row": 0, "column": 0, "sticky": "W", "pady": (0, 4)},
        "configure": {
            "bg": "#434343"
        },
        "label": {
            "text": "",
            "grid": {"row": 0, "column": 0, "sticky": "W"},
            "configure": {
               "width": 20,
                "anchor": "w",
                "bg": "#434343",
                # "fg": "#E8CE78",
                "fg": "#E9E9E9",
                "font": "Helvetica 9",

            }
        },
        "text": {
            "grid": {"row": 0, "column": 1, "sticky": tk.W + tk.E},
            "configure": {
                "width": 90,
                "highlightthickness": "2",
                "highlightbackground": "#535353",
                "relief": "flat",
                "bg": "#393939",
                "fg": "#E9E9E9",
                "font": "Helvetica 9",
                "insertbackground": "#E9E9E9",
                "height": 10
            }
        },
}

button_widget = {
    "name": "",
    "widget_type": "button",
    "grid": {"row": 0, "column": 0, "sticky": "nsew"},
    "configure": {
        "bg": "#434343",
        "text": "",
        "font": "Helvetica 12 bold",
        "fg": "white",
    },
}

# tester = copy.deepcopy(labeled_entry)
# tester["name"] = "tester"
# tester["grid"]["row"] = 0
# tester["label"]["text"] = "Tester"

working_directory = copy.deepcopy(directory_path_entry)
working_directory["name"] = "working_directory"
working_directory["grid"]["row"] = 1
working_directory["label"]["text"] = "Directory Template"

variable_1 = copy.deepcopy(variable)
variable_1["name"] = "variable_1"
variable_1["grid"]["row"] = 2
variable_1["label"]["text"] = "Variable #01"

variable_2 = copy.deepcopy(variable)
variable_2["name"] = "variable_2"
variable_2["grid"]["row"] = 3
variable_2["label"]["text"] = "Variable #02"

variable_3 = copy.deepcopy(variable)
variable_3["name"] = "variable_3"
variable_3["grid"]["row"] = 4
variable_3["label"]["text"] = "Variable #03"

variable_4 = copy.deepcopy(variable)
variable_4["name"] = "variable_4"
variable_4["grid"]["row"] = 5
variable_4["label"]["text"] = "Variable #04"

variable_5 = copy.deepcopy(variable)
variable_5["name"] = "variable_5"
variable_5["grid"]["row"] = 6
variable_5["label"]["text"] = "Variable #05"

variable_6 = copy.deepcopy(variable)
variable_6["name"] = "variable_6"
variable_6["grid"]["row"] = 7
variable_6["label"]["text"] = "Variable #06"

variable_7 = copy.deepcopy(variable)
variable_7["name"] = "variable_7"
variable_7["grid"]["row"] = 8
variable_7["label"]["text"] = "Variable #07"

variable_8 = copy.deepcopy(variable)
variable_8["name"] = "variable_8"
variable_8["grid"]["row"] = 9
variable_8["label"]["text"] = "Variable #08"

variable_9 = copy.deepcopy(variable)
variable_9["name"] = "variable_9"
variable_9["grid"]["row"] = 10
variable_9["label"]["text"] = "Variable #09"

variable_10 = copy.deepcopy(variable)
variable_10["name"] = "variable_10"
variable_10["grid"]["row"] = 11
variable_10["label"]["text"] = "Variable #10"

variable_11 = copy.deepcopy(variable)
variable_11["name"] = "variable_11"
variable_11["grid"]["row"] = 12
variable_11["label"]["text"] = "Variable #11"

variable_12 = copy.deepcopy(variable)
variable_12["name"] = "variable_12"
variable_12["grid"]["row"] = 13
variable_12["label"]["text"] = "Variable #12"

tags = copy.deepcopy(labeled_entry)
tags["name"] = "tags"
tags["grid"]["row"] = 14
tags["label"]["text"] = "Tags"

note = copy.deepcopy(labeled_text)
note["name"] = "note"
note["grid"]["row"] = 15
note["label"]["text"] = "Note"

button = copy.deepcopy(button_widget)
button["name"] = "button"
button["grid"]["row"] = 16
button["configure"]["text"] = "Start"


# steps = copy.deepcopy(directory_path_entry)
# steps["name"] = "steps"
# steps["grid"]["row"] = 14
# steps["label"]["text"] = "Steps"
#
# subdirectories = copy.deepcopy(labeled_entry)
# subdirectories["name"] = "subdirectories"
# subdirectories["grid"]["row"] = 15
# subdirectories["label"]["text"] = "Subdirectories"

configurations = [
    working_directory,
    variable_1,
    variable_2,
    variable_3,
    variable_4,
    variable_5,
    variable_6,
    variable_7,
    variable_8,
    variable_9,
    variable_10,
    variable_11,
    variable_12,
    tags,
    note,
    button
    # steps,
    # subdirectories
]