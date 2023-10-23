# GeoH2-data-prep
Spatial data preparation tools for GeoH2 users. 
These scripts allow users to move from raw data inputs to a GeoH2-ready hexagon input by interfacing with [GLAES](https://github.com/FZJ-IEK3-VSA/glaes/tree/master/) and [SPIDER](https://github.com/carderne/ccg-spider/tree/main). 

## 1 Installation instructions

### 1.1 Clone the repository
First, clone the GEOH2 repository using `git`.

`/your/path % git clone https://github.com/alycialeonard/GeoH2-data-prep.git`

After installation, navigate to the top-level folder of the repo

### 1.2 Install Python dependencies
The Python package requirements to use these tools are in the `requirements.yml` file. 
You can install these requirements in a new environment using `conda` package and environment manager (available for installation [here](https://docs.conda.io/en/latest/miniconda.html)): 

` .../GeoH2-data-prep % conda env create -f requirements.yml`

Then activate this new environment using

`.../GeoH2-data-prep % conda activate geoh2-data-prep`

You are now ready to run the scripts in this repository.

### 1.3 Install Glaes and SPIDER

These pre-processing scripts interface with the Glaes and SPIDER packages.
Please also install these packages with separate environments following the instructions available at the links below. 
- Glaes: https://github.com/FZJ-IEK3-VSA/glaes/tree/master
- Spider: https://github.com/carderne/ccg-spider/tree/main

## 2 Usage instructions

### 2.1 Download input data

Before running the preparation scripts, the data must be downloaded. 

- The global oceans and seas geopackage can be downloaded from: https://www.marineregions.org/downloads.php
- The country boundaries shapefile can be downloaded from: https://www.naturalearthdata.com/downloads/50m-cultural-vectors/50m-admin-0-countries-2/
- OpenStreetMap layers can be downloaded from: https://download.geofabrik.de/africa.html
- The Corine Land Cover dataset can be downloaded from: https://zenodo.org/records/3939050 
- The protected classes dataset can be downloaded from: TO BE ADDED.

Download these files and place them in the `Raw_Spatial_Data` folder.

### 2.2 Define countries to study

These tools can allow you to prepare data for multiple countries at once. 
To define what countries to look at, take the following two steps:
- Modify the list `country_names` in `spatial_data_prep.py` and `combine_glaes_spider.py` to contain the names of all the countries for which you want to prepare data.
- Take the template `Country_config.yml` under `Inputs_Spider`. Make a duplicate for each country of interest with the word `Country` replaced with the country name without periods or spaces.

Note that the spellings used for country names must match those used in the Natural Earth country boundaries shapefile. 

### 2.3 Run initial data prep

From `GeoH2-data-prep`, run `spatial_data_prep.py`:

`.../GeoH2-data-prep % python spatial_data_prep.py`

This will pre-process the raw data and place the prepared versions in the `Inputs_Glaes` and `Inputs_Spider` folders.

### 2.4 Run Glaes

Take the contents of the `Inputs_Glaes` folder and copy them into your Glaes repository at the top level.
You can then move to your glaes directory, activate your glaes environment, and run the script `workflow.py`:

`.../glaes % python workflow.py`

This will produce files with the format `Country_turbine_placements.shp` and `Country_pv_placements.shp` under the folder `processed`.
Copy the folder `processed` from the Glaes repository back to this repository, under `Inputs_Glaes/processed`.

### 2.5 Run Spider

Take the contents of the `Inputs_Spider` folder and copy them into your spider repository under `/prep`
You can then move to this directory, activate your spider environment, and run the spider CLI. 
Take the following command, replace the `Country` with the name of the country you are studying without spaces or periods, and paste it in your terminal:

`.../prep % gdal_rasterize data/Country.gpkg -burn 1 -tr 0.1 0.1 data/blank.tif && gdalwarp -t_srs EPSG:4088 data/blank.tif data/blank_proj.tif && spi processed/Country_hex.geojson`

This command must be issued for each country to be studied. 
You can "daisy chain" the commands for multiple countries together using the `&&` operator.
This will produce a set of hexagon tiles for each country using the parameters in the config file.
They will be saved in the folder `processed`.
Copy this folder back to this repository under `Inputs_Spider\processed`.

### 2.6 Combine Glaes and Spider results for GeoH2

The spatial data can then be combined into a final hexagon file for use in GeoH2 using the `combine_glaes_spider.py` script:

`.../GeoH2-data-prep % python combine_glaes_spider.py`

This will save a file with the format `Country_hex_final.geojson` to the folder `Inputs_GeoH2\Data`.
This can then be pasted into a copy of the `GeoH2` repository as your baseline input data for modelling. 




