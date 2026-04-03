# README File

Created by: EPA133a Group 01

|        Name        | Student Number |
|:------------------:|:---------------|
| Niels van den Dool | 5026717        |
|    Eli Kapteijn    | 6587380        |
|    Nick Schreurs    | 6581951        |
|    Lieke Wahlen    | 5179564        |
|    Mirte Wildeboer    | 5326265        |


## Overview
This repository contains the model, data, and experimental setup for Assignment 4 of the EPA133a Advanced Simulation course. 
The project focuses on assessing the criticality of bridges using the Mesa framework (version 2.1.4) in Python.

### Project Objective
The primary goal of this simulation is to automatically generate a model to study the effects of natural disasters and unavailability of bridges on traffic throughput in Bangladesh. 
Specifically, the model simulates goods transport (trucks) along the economically vital N1&N2 highways and all its large sideroads. 
Because bridges play a crucial role in Bangladesh's transport network and are vulnerable to disruptions, this model analyzes how varying bridge qualities (Categories A, B, C, and D) and natural disaster risk-factors impact overall travel delays in the road network.

## How to Use

**1. Prepare the Data**
Run `notebook/1_read_traffic_data.ipynb` and `notebook/2_data_preparation_with_AADT.ipynb` in sequential order to prepare the necessary dataset. Executing these notebook generates the necessary CSV input file required for the agent-based model.

**1a Include vulnerability data**
Then to add the geographical data to the csv, the software tool Qgis was used to add columns on elevation, distance to water bodies and historical cyclone data.
The Qgis project including its layer data and model is included in the `qgis` folder. Unzip the folder and connect to the geopackage in Qgis.
Open the 'Bridge vulnerability' project and open the Processing Toolbox. Go to 'Project models' and execute the 'Qgis vulnerability data' model.
The model asks for input layers, which are the provided layers for the AADT input csv, cyclone data, digital elevation model and waterways.
After running the model, the final_processed_layer can be manually exported to a .csv file.


**2. Run the Simulation**
Execute `model/model_run.py` to run the model without the visualization interface. You can configure various parameters within the script, including:
* Specific scenarios to run
* Number of replications (simulations)
* Total amount of model steps
* Starting seed

**Expected Output:** The model generates a separate CSV file for each scenario and saves it to the `experiment` folder. These files log the average driving time for each replication, identified by their unique starting seeds.

**3. Analyze the Results**
Run the notebooks 3a, 3b, 3c to analyze the experimental data and generate the visualizations used in our final analysis.

---

## Documentation
You can find our full analysis, discussion on limitations, and write-up in the `report` folder. Happy reading!