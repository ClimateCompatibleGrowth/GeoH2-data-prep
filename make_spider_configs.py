# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 15:53:20 2023

@author: Alycia Leonard, University of Oxford

make_spider_configs.py

This script makes SPIDER configs for each country in the country_names list.
It saves these files as Country_config.yml under Inputs_Spider/configs.
"""

import yaml
import os
from unidecode import unidecode

# Define the list of countries to replace "Country" with
country_names = ["REPLACE", "WITH", "COUNTRY", "NAMES"]

# Get path to this file
dirname = os.path.dirname(__file__)
input_file = os.path.join(dirname, "Inputs_Spider", "Country_config_hydro.yml")
save_path = os.path.join(dirname, "Inputs_Spider", "configs")


# Open and load the input YAML file
with open(input_file, 'r') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)


# Define a function to recursively replace "Country" with a country name
def replace_country(node, country):
    if isinstance(node, dict):
        return {key: replace_country(value, country) for key, value in node.items()}
    elif isinstance(node, list):
        return [replace_country(item, country) for item in node]
    elif isinstance(node, str):
        return unidecode(node).replace("Country", country)
    else:
        return node


# Create and save separate .yml files for each country
for country in country_names:
    print(f'Prepping config file for {country}...')
    # Get country names without accents, spaces, apostrophes, or periods for SPIDER
    country_name_clean = unidecode(country)
    country_name_clean = country_name_clean.replace(" ", "")
    country_name_clean = country_name_clean.replace(".", "")
    country_name_clean = country_name_clean.replace("'", "")

    output_file = f"{country_name_clean}_config.yml"

    current_data = replace_country(data, country_name_clean)

    with open(os.path.join(save_path, output_file), 'w', encoding='utf-8') as file:
        yaml.dump(current_data, file, default_flow_style=False, allow_unicode=True)

    print(f'Config file is created and saved as "{output_file}"!')
