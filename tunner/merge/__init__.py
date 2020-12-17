import shutil
import glob
import json
import os


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
        return self._copy()

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
        buffer = []
        for id, tunner_file in self.source_files.items():
            if not id in self.destination_files:
                source_directory_path = os.path.dirname(tunner_file.path)
                destination_directory_path = self._evaluate_destination_path(tunner_file)
                # os.makedirs(destination_directory_path, exist_ok=True)
                shutil.copytree(source_directory_path, destination_directory_path)
                print("%s -> %s" % (source_directory_path, destination_directory_path))
                buffer.append({"source": source_directory_path, "destination": destination_directory_path})
        return buffer

    def _evaluate_destination_path(self, tunner_file):
        path_items = [self.cfg["destination"]]
        for path_variable in self.cfg["path_items"]:
            path_item = self._tunner_variable_value(path_variable, tunner_file.generate["variables"])

            if path_item.strip() != "":
                path_items.append(path_item)

        path_items.append(os.path.basename(os.path.dirname(tunner_file.path)))
        return os.path.join(*path_items)

    def _tunner_variable_value(self, name, variables):
        variable = [variable for variable in variables if variable["name"] == name][0]
        return variable["value"]