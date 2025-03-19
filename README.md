# GeoH2-data-prep
Spatial data preparation tools for [GeoH2](https://github.com/ClimateCompatibleGrowth/GeoH2) users. 
The GeoH2 library requires spatial hexagon files for the area of interest with several spatial parameters attached as an input. 
These scripts are built to assist in creating these input data. 
They allow users to move from raw data inputs to a GeoH2-ready hexagon input by interfacing with the Global Land Availability of Energy Systems ([GLAES](https://github.com/FZJ-IEK3-VSA/glaes/tree/master/)) and Spatially Integrated Development of Energy and Resources ([SPIDER](https://github.com/carderne/ccg-spider/tree/main)).

> [!NOTE]
> Please note that when using this codebase, users may need to modify the filenames and paths included in the scripts should new releases of the suggested data be made or should the user choose to use different/supplementary data sources.
___
## 1 Installation instructions

### 1.1 Clone the repository and submodules
First, clone the repository and initialise the submodules in one:

`/your/path % git clone --recurse-submodules https://github.com/ClimateCompatibleGrowth/GeoH2-data-prep.git`

After cloning, navigate to the top-level folder of the repository.

### 1.2 Install Python dependencies
The Python package requirements to use these tools are in the `environment.yaml` file. 
You can install these requirements in a new environment using `mamba` package and environment manager (installation instructions [here](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html)): 

` .../GeoH2-data-prep % mamba env create -f environment.yaml`

This new environment can be activated using:

`.../GeoH2-data-prep % mamba activate data-prep`

Make sure to deactivate the environment before the next step.

### 1.3 Install Spider environment
You will need to create a separate environment for the Spider submodule to work.

Firstly, navigate to the `ccg-spider/prep` folder:

`.../GeoH2-data-prep % cd ccg-spider/prep`

Next, create a new environment using your package and environment manager. Below is how you can using `mamba`:

`.../prep % mamba create -n spider`

Next, activate the environemtn using:

`.../prep % mamba activate spider`

Next, install some packages:

`.../prep % mamba install pip gdal`

Next, install the spider requirements:

`.../prep % pip install -e .`

You should now have a fully functioning environment named `spider`. You can deactivate this for now and return to the top-level of the repository.
___
## 2 Preparing input data

### 2.1 Download input data

Before running the preparation scripts, the data must be downloaded. 

- The global oceans and seas geopackage can be downloaded from: https://www.marineregions.org/downloads.php
- The country boundaries shapefile can be downloaded from: https://www.naturalearthdata.com/downloads/50m-cultural-vectors/50m-admin-0-countries-2/
- OpenStreetMap Shapefile layers can be downloaded from: https://download.geofabrik.de/africa.html
- The Corine Land Cover dataset can be downloaded from: https://zenodo.org/records/3939050

Download these files and place them in the `data` folder.
For OpenStreetMap files, please extract the .shp.zip folder for each country to a subfolder `OSM\[CountryName]` under `data`.
For the global oceans and seas geopackage, please save the `goas_v01.gpkg` file to a subfolder `GOaS_v1_20211214_gpkg` under `data`.

### 2.2 Hydropower input data (optional)

If you want hydropower to be used as a generator, you will need another input file.
It should be named `[CountryName]_hydropower_plants.csv` and placed in the `data` folder. There is a template which you can use in the `data` folder with some dummy data in.
You can also use files from **open-source datasets** like the [Hydropower Database](https://github.com/energy-modelling-toolkit/hydro-power-database). You **must** change the file name to match `[CountryName]_hydropower_plants.csv` and the column titles must be changed to match those in the template file. 

#### **Input Data Requirements**
- The script is designed for datasets containing:
  - **Latitude & Longitude** (plant location)
  - **Installed capacity (MW)**
  - **Annual generation (GWh)**
  - **Plant type** (e.g., HDAM, HPHS)
  - **Hydraulic head (m)**

## 3 Running data prep

There are two main scripts that are used as well as the Spider submodule.

### 3.1 Run initial data prep before Spider
>[!NOTE]
> Remember to activate the `prep` environment.

There are some arguments that you need to pass via the CLI. They are:
- `countries`: At least one required. This should be the name of the countries you are prepping with a space between them. Make sure that the spellings used for country names match those used in the Natural Earth country boundaries shapefile.
- `--hydro`: Default is False, so only use this when you need to change to True.

Below is an example of what you could run (with `Country1` and `Country2` being real country names):

`.../GeoH2-data-prep % python prep_before_spider.py Country1 Country2 --hydro True`

The above will firstly prepare a hydropower Geopackage (GPKG), then pre-process the raw data and create a spider config and lastly, it will run GLAES. It will do that for each country provided.

### 3.2 Run Spider

Now you will need to move to the `ccg-spider/prep` directory, activate your `spider` environment, and run the spider CLI. 

Take the following command, replace the `Country` with the name of the country you are studying without spaces or periods, and paste it in your terminal:

`.../prep % gdal_rasterize data/Country.gpkg -burn 1 -tr 0.1 0.1 data/blank.tif && gdalwarp -t_srs EPSG:4088 data/blank.tif data/blank_proj.tif && spi --config=Country_config.yml Country_hex.geojson`

This command must be ran for **each** country.
This will produce a set of hexagon tiles for each country using the parameters in the config file.

>[!IMPORTANT]
> Do not use `&&` to run all the countries at once, it will not produce new .tif files thus producing inaccurate hexagon files.

### 3.3 Run data prep after spider

>[!NOTE]
> Remember to move back to the top-level folder and to activate the `prep` environment, after deactivating the `spider` environment.

There are some arguments that you need to pass via the CLI. They are:
- `countries`: At least one required. This should be the name of the countries you are prepping with a space between them. Make sure that the spellings used for country names match those used in the Natural Earth country boundaries shapefile.
- `-ic`: At least one required. This is the two-letter ISO code for your countries. They must be in the same order are your countries.

Below is an example of what you could run (with `Country1` and `Country2` being real country names and `C1` and `C2` being real 2-letter ISO Codes for each country respectively):

`.../GeoH2-data-prep % python prep_before_spider.py Country1 Country2 -ic C1 C2`

The above will combine the Spider and GLAES files, creating `[Country]_hex_final.geojson` files for each country. It will then assign an interest rate to different hexagons for different technology categories based on their country. Lastly, this script removes the duplicated hexagons that belong to a country which are not the desired country.

This will save files with the format `hexagons_with_country_[ISOCode].geojson` to the folder `inputs_geox\data`.
This can then be pasted into a copy of the `Geo-X` repository as your baseline input data for modelling. 
___

## Citation

If you decide to use this library and/or GeoH2, please kindly cite us using the following: 

*Halloran, C., Leonard, A., Salmon, N., Müller, L., & Hirmer, S. (2024). 
GeoH2 model: Geospatial cost optimization of green hydrogen production including storage and transportation. 
Pre-print submitted to MethodsX: https://doi.org/10.5281/zenodo.10568855. 
Model available on Github: https://github.com/ClimateCompatibleGrowth/GeoH2.*

```commandline
@techreport{halloran2024geoh2,
author  = {Halloran, C and Leonard, A and Salmon, N and Müller, L and Hirmer, S},
title   = {GeoH2 model: Geospatial cost optimization of green hydrogen production including storage and
transportation},
type = {Pre-print submitted to MethodsX},
year    = {2024},
doi = {10.5281/zenodo.10568855},
note = {Model available on Github at https://github.com/ClimateCompatibleGrowth/GeoH2.}
}
```
___

