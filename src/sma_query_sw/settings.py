# -*- coding: utf-8 -*-

import os
import json
from pathlib import Path


def get_settings_from_file():
    settings_search = [f"{Path.home()}/.sma_mqtt/settings.json", "/etc/sma_mqtt/settings.json"]
    settings_path = None

    for settings_file in settings_search:
        if os.path.exists(settings_file):
            settings_path = settings_file
            break

    if not settings_path:
        raise FileNotFoundError("Settings file not found")

    with open(settings_path, "r") as read_settings:
        settings = json.load(read_settings)

    return settings
