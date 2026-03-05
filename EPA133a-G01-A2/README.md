# Example README File

Created by: EPA133a Group 01

|        Name        | Student Number |
|:------------------:|:---------------|
| Niels van den Dool | 5026717        |
|    Eli Kapteijn    | 6587380        |
|    Nick Schreurs    | 6581951        |
|    Lieke Wahlen    | 5179564        |
|    Mirte Wildeboer    | 5326265        |


## Introduction

Every project should have a README file to help a first-time user understand what it is about and how they might be able to use it. 
This file is where you (as a group) shall provide the information needed by the TAs to evaluate and grade your work.

If you are looking for information about the Demo model of Assignment 2, navigate to the [model/README.md](model/README.md) in the [model](model) directory. Have **fun** modeling in Python!

## How to Use

1. To prepare the bridges dataset from Bangladesh, the notebook [notebooks/1_data_cleaning.ipynb](notebooks/1_data_cleaning.ipynb) was used.
After running this notebook, a CSV-file (comma-separated values) is generated that can be used as input for the model provided in this assignment.
2. Run the [model/model_run.py](model/model_run.py) with the parameters for scenarios, amount of simulations, amount of model steps and starting seed.
The output of this model can be found in the folder [experiment](experiment) where for each scenario a different CSV-file is generated with the average driving time for each simulation (identified with the different seeds).
3. To analyse the data and include visualisations in the report, an additional notebook [notebooks/2_results_scenario.ipynb](notebooks/2_results_scenario.ipynb) was made/used.

The report can be found in the [report](report) folder. Happy reading!