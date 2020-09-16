import argparse
import os
import json
import datetime
import platform
import socket
import uuid
import alphabetic_timestamp as ats
import time
import glob
import shutil

try:
    import Tkinter as tk
except Exception as e:
    import tkinter as tk

from . import gui


class Path(object):
    @classmethod
    def package_directory(cls):
        return os.path.dirname(os.path.abspath(__file__))

    @classmethod
    def configuration_directory(cls):
        return os.path.join(cls.package_directory(), "configuration")

    @classmethod
    def starter_configuration(cls):
        return os.path.join(cls.configuration_directory(), "starter.json")

    @classmethod
    def copier_configuration(cls):
        return os.path.join(cls.configuration_directory(), "cp.json")


class DataFiller(object):
    def __init__(self):
        self.gui = None
        self.cfg = None

    def fill(self, gui, cfg):
        self.gui = gui
        self.cfg = cfg

        self._fill_working_directory()
        self._fill_variables()
        self._fill_tags()
        self._fill_notes()

    def _fill_working_directory(self):
        self.gui.working_directory.entry_string.set(self.cfg["working_directory"])

    def _fill_variables(self):
        for cfg, widget in zip(self.cfg["variables"], self.gui.variables):
            widget.variable_string.set(cfg["name"])
            widget.value_string.set(cfg["value"])
            self._fill_check_button(widget, cfg)

    def _fill_check_button(self, widget, cfg):
        if "checked" in cfg:
            if cfg["checked"] == "True" or cfg["checked"] == "1":
                widget.checkbox_variable.set(1)
            else:
                widget.checkbox_variable.set(0)
        else:
            widget.checkbox_variable.set(0)

    def _fill_tags(self):
        self.gui.tags.entry_string.set(", ".join(self.cfg["tags"]))

    def _fill_notes(self):
        self.gui.note.text.delete(1.0, "end")
        self.gui.note.text.insert(1.0, "\n".join(self.cfg["note"]))


class Binder(object):
    def __init__(self):
        pass

    def bind(self, gui, controller):
        gui.button.button.bind("<Button-1>", controller.button_click)


class TunnerFile(object):
    def __init__(self):
        self.gui = None

    def content(self, gui, specific_time):
        self.gui = gui
        return {
            "id": ats.base62.from_datetime(specific_time, time_unit=ats.TimeUnit.seconds),

            "time": {
                "str": str(specific_time),
                "epoch": specific_time.timestamp(),
                "zone": str(time.tzname)
            },

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

            "tags": self._tags(),

            "variables": self._variables(),

            "note": self._note()

        }

    def _tags(self):
        return [tag.strip() for tag in self.gui.tags.entry.get().split(",")]

    def _variables(self):
        variables = []

        for variable in self.gui.variables:
            v = {}
            v["name"] = variable.variable_string.get().strip()
            v["value"] = variable.value_string.get().strip()
            v["checked"] = variable.checkbox_variable.get()

            variables.append(v)

        return variables

    def _note(self):
        return self.gui.note.text.get("1.0","end")


class StarterController:
    def __init__(self):
        self.cfg = None
        self.gui = None
        self.root = None
        self.data_filler = DataFiller()
        self.binder = Binder()
        self.specific_time = None
        self.directory_path = None

    def run(self, arguments):
        self.root = tk.Tk()
        self.gui = gui.starter.build(self.root)
        self._read_configuration()
        self.data_filler.fill(self.gui, self.cfg)
        self.binder.bind(self.gui, self)
        self.root.mainloop()

    def _read_configuration(self):
        with open(Path.starter_configuration()) as cfg_file:
            self.cfg = json.load(cfg_file)

    def button_click(self, event):
        # self._disabled_button()
        self._get_specific_time()
        self._evaluate_directory_path()
        self._create_working_directory()
        self._write_tunner_file()
        print(self.directory_path)
        # self._enabled_button()

    def _create_working_directory(self):
        os.makedirs(self.directory_path, exist_ok=True)

    def _write_tunner_file(self):
        tf = TunnerFile()

        with open(self._tunner_file_path(), "w+") as f:
            json.dump(tf.content(self.gui, self.specific_time), f, indent=4, sort_keys=True)

    def _get_specific_time(self):
        self.specific_time = datetime.datetime.now()

    def _evaluate_directory_path(self):
        template = self.gui.working_directory.entry.get()
        path = self.specific_time.strftime(template)

        for variable in self.gui.variables:
            if variable.checkbox_variable.get():
                path = path.replace(variable.variable_string.get().strip(), variable.value_string.get().strip())

        self.directory_path = path

    def _tunner_file_path(self):
        return os.path.join(self.directory_path, ".tunner")

    def _disabled_button(self):
        self.gui.button.button.configure(text="working", bg="#737373")
        self.gui.button.button["state"] = "disabled"

    def _enabled_button(self):
        self.gui.button.button.configure(text="Start", bg="#434343")
        self.gui.button.button["state"] = "normal"


class TunnerFileContent:
    def __init__(self):
        self.path = None
        self.content = None

    @property
    def id(self):
        return self.content["id"]


class CopierController(object):
    def __init__(self):
        self.cfg = None
        self.source_tunner_file_paths = None
        self.destination_tunner_files_paths = None
        # TODO: danger
        self.source_files = {}
        self.destination_files = {}

    def run(self, arguments):
        self._read_configuration(arguments.configuration)
        self._find_all_tunner_files()
        self._load_content_all_tunner_files()
        self._copy()

    def _read_configuration(self, path):
        with open(path) as cfg_file:
            self.cfg = json.load(cfg_file)

    def _find_all_tunner_files(self):
        self.source_tunner_file_paths = self._find_all_tunner_files_in_directory(self.cfg["source"])
        self.destination_tunner_files_paths = self._find_all_tunner_files_in_directory(self.cfg["destination"])

    def _find_all_tunner_files_in_directory(self, directory):
        path = os.path.join(directory, "**", ".tunner")
        return glob.glob(path, recursive=True)

    def _load_content_all_tunner_files(self):
        self._load_content_tunner_files(self.source_files, self.source_tunner_file_paths)
        self._load_content_tunner_files(self.destination_files, self.destination_tunner_files_paths)

    def _load_content_tunner_files(self, source_files, tunner_file_paths):
        for tunner_path in tunner_file_paths:
            tf = TunnerFileContent()
            tf.path = tunner_path
            tf.content = self._read_tunner_file(tunner_path)
            source_files[tf.id] = tf

    def _read_tunner_file(self, path):
        with open(path) as tf:
            return json.load(tf)

    def _copy(self):
        for id, tunner_file in self.source_files.items():
            if not id in self.destination_files:
                source_directory_path = os.path.dirname(tunner_file.path)
                destination_directory_path = self._evaluate_destination_path(tunner_file)
                # os.makedirs(destination_directory_path, exist_ok=True)
                shutil.copytree(source_directory_path, destination_directory_path)
                print("%s -> %s" % (source_directory_path, destination_directory_path))

    def _evaluate_destination_path(self, tunner_file):
        path_items = [self.cfg["destination"]]
        for path_variable in self.cfg["path_items"]:
            path_item = self._tunner_variable_value(path_variable, tunner_file.content["variables"])

            if path_item.strip() != "":
                path_items.append(path_item)

        path_items.append(os.path.basename(os.path.dirname(tunner_file.path)))
        return os.path.join(*path_items)

    def _tunner_variable_value(self, name, variables):
        variable = [variable for variable in variables if variable["name"] == name][0]
        return variable["value"]


def main():
    starter = StarterController()
    copier = CopierController()

    parser = argparse.ArgumentParser(description="TUNNER: PRE-ALPHA VERSION",
                                     formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers()

    starter_parser = subparsers.add_parser('starter')
    starter_parser.set_defaults(func=starter.run)

    copier_parser = subparsers.add_parser('cp')
    copier_parser.add_argument('-c', "--configuration", type=str, default=Path.copier_configuration())
    copier_parser.set_defaults(func=copier.run)

    arguments = parser.parse_args()
    arguments.func(arguments)


if __name__ == "__main__":
    main()