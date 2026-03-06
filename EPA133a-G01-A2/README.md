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
This repository contains the model, data, and experimental setup for Assignment 2 of the EPA133a Advanced Simulation course. 
The project focuses on building a data-driven, agent-based simulation using the Mesa framework (version 2.1.4) in Python.

### Project Objective
The primary goal of this simulation is to automatically generate a model to study the effects of bridge maintenance and unavailability on traffic throughput in Bangladesh. 
Specifically, the model simulates goods transport (trucks) along the economically vital N1 highway, traveling from Chittagong to Dhaka.
Because bridges play a crucial role in Bangladesh's transport network and are vulnerable to disruptions, this model analyzes how varying bridge qualities (Categories A, B, C, and D) impact overall travel delays.

## How to Use

**1. Prepare the Data**
Run the `notebooks/1_data_cleaning.ipynb` notebook to clean the Bangladesh bridges dataset. Executing this notebook generates the necessary CSV input file required for the simulation.

**2. Run the Simulation**
Execute `model/model_run.py` to run the model without the visualization interface. You can configure various parameters within the script, including:
* Specific scenarios to run
* Number of replications (simulations)
* Total amount of model steps
* Starting seed

**Expected Output:** The model generates a separate CSV file for each scenario and saves it to the `experiment` folder. These files log the average driving time for each replication, identified by their unique starting seeds.

**3. Analyze the Results**
Run the `notebooks/2_results_scenario.ipynb` notebook to analyze the experimental data and generate the visualizations used in our final analysis.

---

## Documentation
You can find our full analysis, discussion on limitations, and write-up in the `report` folder. Happy reading!