# -*- coding: utf-8 -*- 
"""
Created on Tue Aug 6 11:32:11 2024

@author:
Lukas Schirren, Imperial College London

This script prepares raw spatial data for hexagon preparation in SPIDER by creating a geopackage file.
The raw inputs should be in CSV format, such as the JRC hydro power plant database.
The outputs are saved in /Inputs_Spider/data.

"""

import os
import pandas as pd 
import geopandas as gpd
from pyproj import Transformer

def convert_coordinates(easting, northing):
    longitude, latitude = transformer.transform(easting, northing)
    return latitude, longitude


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))  
    input_path = os.path.join(script_dir, "Raw_Spatial_Data", "jrc-hydro-power-plant-database.csv")
    output_dir = os.path.join(script_dir, "Inputs_Spider", "data")
    os.makedirs(output_dir, exist_ok=True) 
    output_path = os.path.join(output_dir, "hydropower_dams_EU.gpkg")

    data = pd.read_csv(input_path)

    data = data[['id', 'lat', 'lon', 'name', 'type', 
                 'installed_capacity_MW', 'avg_annual_generation_GWh', 
                 'head', 'country_code']]

    data['lon'] = pd.to_numeric(data['lon'], errors='coerce')
    data['lat'] = pd.to_numeric(data['lat'], errors='coerce')

    data = data.rename(columns={
        "installed_capacity_MW": "capacity",
        "lat": "Latitude",
        "lon": "Longitude",
        "type": "plant_type"
    })

    data = data.dropna(subset=['Longitude', 'Latitude'])

    data = data[data['plant_type'].isin(['HDAM', 'HPHS'])]
    data['capacity'] = pd.to_numeric(data['capacity'], errors='raise')

    data_existing = data.dropna(subset=['head'])
    print(f"Number of missing 'head' values: {data_existing['head'].isna().sum()}")

    gdf = gpd.GeoDataFrame(
        data_existing,
        geometry=gpd.points_from_xy(data_existing.Longitude, data_existing.Latitude)
    )

    gdf.set_crs(epsg=4326, inplace=True)
    gdf.to_file(output_path, layer='dams', driver="GPKG")

    relative_output_path = os.path.relpath(output_path, script_dir)
    print(f"GeoPackage file successfully created at: {relative_output_path}")
