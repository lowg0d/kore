import json
import logging
import os
from typing import Any, Dict

CONFIG_PATH = "./src/config"


class Config:
    def __init__(self) -> None:
        self.log = logging.getLogger("kore.config")
        self.log.debug("Loading configuration manager...")

        self.loaded_data = {}
        self._load_files()

    def get(self, keys: str, file_name: str = "config", default: Any = None) -> Any:
        """
        Accesses nested configuration data using a hierarchical key structure.

        Args:
            keys (str): A string representing the hierarchical keys separated by '.',
                        e.g., 'parent.child.key' to access data['parent']['child']['key'].
            file_name (str): The filename (without extension) of the JSON configuration to access.

        Returns:
            The value from the configuration data matching the hierarchical keys,
            or None if the file or keys do not exist.
        """
        if not self._is_loaded(file_name):
            return

        data = self.loaded_data[file_name]
        key_list = keys.split(".")

        for key in key_list:
            # if key does not exist
            if key not in data:
                self.log.error(f"({key}) is not valid key for ({file_name}.json)")
                return default

            data = data[key]

        return data

    def put(self, keys: str, new_value: Any, file_name: str = "config") -> None:
        """Modifies nested configuration data using a hierarchical key structure.

        Args:
            keys (str): A string representing the hierarchical keys separated by '.',
                    for the location where the value should be set,
                    e.g., 'parent.child.key' to access data['parent']['child']['key']..
            new_value (Any): The new value to set at the specified location in the configuration data.
            file_name (str, optional): The filename (without extension) of the JSON configuration to modify.. Defaults to "private".
        """
        if not self._is_loaded(file_name):
            return

        data = self.loaded_data[file_name]
        current = data

        key_list = keys.split(".")
        for key in key_list[:-1]:
            # if key does not exist
            if key not in current:
                self.log.error(f"({key}) is not valid key for ({file_name}.json)")
                return

            current = current[key]

        current[key_list[-1]] = new_value
        if file_name == "settings":
            path = file_name + ".json"
        else:
            path = os.path.join(CONFIG_PATH, (file_name + ".json"))

        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    def _is_loaded(self, file_name: str) -> bool:
        """Checks if the specified file's data is loaded into the configuration data map."""

        if file_name not in self.loaded_data.keys():
            self.log.error(
                f"'{file_name}' is was not loaded at the application start !"
            )
            return False

        else:
            return True

    def _load_files(self) -> None:
        """Loads all the JSON configuration files in the configuration directory."""

        self.log.debug("Loading config files...")
        files_to_load = [_file for _file in os.listdir(CONFIG_PATH)]

        for complete_file_name in files_to_load:
            file_name = complete_file_name.replace(".json", "")
            path = os.path.join(CONFIG_PATH, complete_file_name)
            data = self._load_json_file(path)

            self.loaded_data[file_name] = data

        self.log.debug(f"Loaded files: {files_to_load}")

    def _load_json_file(self, path: str) -> Any:
        """
        Loads a JSON file and returns its content. If the file is not a valid JSON,
        an empty dictionary is returned.

        Args:
            path (str): The path to the JSON file.

        Returns:
            Any: The content of the JSON file, or an empty dictionary if the file is invalid.
        """
        try:
            with open(path, mode="r", encoding="utf-8") as _file:
                self.log.debug(f"'{path}' Loaded !")
                return json.load(_file)
        except (json.JSONDecodeError, FileNotFoundError, OSError):
            self.log.error(f"Not able to read format from '{path}'")
            return {}

    def runtime_load(self, path: str) -> Any:
        file_name = path.replace(".json", "").replace("./", "")
        data = self._load_json_file(path)
        self.loaded_data[file_name] = data

        self.log.debug(f"Loaded files: {self.loaded_data.keys()}")
