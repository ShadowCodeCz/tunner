import os
import json


class ConfigurationType:
    gui = "gui"
    previous = "previous"


class AutoConfiguration:
    def __init__(self):
        self.file_of_type = {
            ConfigurationType.gui: "gui.json",
            ConfigurationType.previous: "previous.json"
        }

    def load(self, type, current_python_file):
        path = self.configuration_file_path(type, current_python_file)
        with open(path) as f:
            return json.load(f)

    def load_gui_cfg(self, current_python_file):
        return self.load(ConfigurationType.gui, current_python_file)

    def load_previous_cfg(self, current_python_file):
        return self.load(ConfigurationType.previous, current_python_file)

    def write_previous_cfg(self, content, current_python_file):
        path = self.configuration_file_path(ConfigurationType.previous, current_python_file)
        with open(path, "w+") as f:
            json.dump(content, f, indent=4)

    def configuration_file_path(self, type, current_python_file):
        directory = os.path.abspath(os.path.dirname(current_python_file))
        return os.path.join(directory, self.file_of_type[type])