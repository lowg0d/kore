import json
import logging
import os

from PySide6.QtWidgets import QLabel, QVBoxLayout

from ..components import SettingFormWidget
from ..managers import Config


class DynamicConfigManager:

    def __init__(
        self,
        config_instance: type[Config],
        destination_layout: type[QVBoxLayout],
        settings_widget: type[SettingFormWidget] = SettingFormWidget,
        config_path: str = "./src/config",
    ) -> None:
        self.log = logging.getLogger("kore.dynamic_config")
        self.config_path = config_path

        self.config_instance = config_instance
        self.config_instance.runtime_load(path="./settings.json")

        self.settings_widget_class = settings_widget
        self.destination_layout = destination_layout

        with open(os.path.join(self.config_path, "conf_metadata.json"), "r") as f:
            self.metadata = json.loads(f.read())

        self._check_structure()
        self._sync_settings()

    def generate(self):
        for category, setting in self.metadata.items():
            category_name = category.replace("_", " ").lower().capitalize()
            label = QLabel(category_name)
            label.setObjectName("category_title")
            self.destination_layout.addWidget(label)
            for key, data in setting.items():
                widget = self.settings_widget_class(
                    f"{category}.{key}", data, self.config_instance
                )
                self.destination_layout.addWidget(widget)

    def _merge_settings(
        self, current_settings: dict, settings_from_metadata: dict
    ) -> dict:
        merged_settings = {}

        for category, metadata_settings in settings_from_metadata.items():
            # Only add categories present in metadata
            if category in current_settings:
                # Create a sub-dict for the category
                merged_category = {}
                current_category = current_settings[category]

                for key, metadata_value in metadata_settings.items():
                    # If the key exists in both, take the value from current_settings
                    if key in current_category:
                        merged_category[key] = current_category[key]
                    else:
                        # If the key doesn't exist in current_settings, take metadata value
                        merged_category[key] = metadata_value

                merged_settings[category] = merged_category
            else:
                # If the category is missing in current, take the entire category from metadata
                merged_settings[category] = metadata_settings

        merged_settings["file_version"] = "0.0.1"
        return merged_settings

    def _sync_settings(self):
        """sync settings with the metadata (remove the ones that dont exist etc...)"""
        with open("settings.json", "r") as f:
            try:
                current_settings = json.loads(f.read())
            except:
                self.log.error(
                    f"unable to read 'settings.json' (corrupted file) using default values"
                )
                current_settings = {}

        settings_from_metadata = {}
        for category, settings in self.metadata.items():
            settings_from_metadata[category] = {}

            for setting in settings:
                settings_from_metadata[category][setting] = settings[setting][
                    "default_value"
                ]

        merged = self._merge_settings(current_settings, settings_from_metadata)

        with open("settings.json", "w") as f:
            try:
                json.dump(merged, f, indent=4)
            except Exception as e:
                self.log.error(
                    f"error dumping new settings into the settings.json: {e}"
                )

    def _check_structure(self):
        os.makedirs(self.config_path, exist_ok=True)
        files = ["settings.json", os.path.join(self.config_path, "conf_metadata.json")]
        for f in files:
            if not os.path.exists(f):
                self.log.warning(f"'{f}' not found, creating empty !")
                with open(f, "w") as file:
                    json.dump({}, file)
