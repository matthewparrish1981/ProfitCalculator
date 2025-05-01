import json
import os
import pandas as pd

CONFIG_FILE = "config.json"
CALCULATIONS_FOLDER = "calculations"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"products": [], "shipping_options": ["Sea", "Air"], "exchange_rate": 1.25, "shipping_cost_per_unit_3pl": 2.00}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config_data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)

# Additional functions would follow...
