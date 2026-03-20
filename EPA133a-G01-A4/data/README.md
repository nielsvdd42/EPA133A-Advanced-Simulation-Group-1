# Data for Model Generation of Simple Transport Model Demo in MESA

Created by:
Yilin HUANG

Email:
y.huang@tudelft.nl

Edited by:

|        Name        | Student Number |
|:------------------:|:---------------|
| Niels van den Dool | 5026717        |
|    Eli Kapteijn    | 6587380        |
|    Nick Schreurs    | 6581951        |
|    Lieke Wahlen    | 5179564        |
|    Mirte Wildeboer    | 5326265        |


Version:
1.1

## Introduction

The simple transport model demo, see [../model/model.py](../model/model.py) for EPA133a Advanced Simulation course Assignment 3, takes a `csv` input data file that specifies the infrastructure model components to be generated. The data format used **by the demo model** is described here.

## Format

|     Column | Description                                              |
| ---------: | :------------------------------------------------------- |
|       road | On which road does the component belong to               |
|         id | **Unique ID** of the component                           |
| model_type | Type (i.e. class) of the model component to be generated |
 | condition| Condition of the object, determines the change of breaking down|
|       name | Name of the object                                       |
|        lat | Latitude in Decimal Degrees                              |
|        lon | Longitude in Decimal Degrees                             |
|     length | Length of the object in meters                           |

The column `road` is used by the model generation to classify model components by roads, i.e., on which road does a component belong to. The model generation assumes that the infrastructure model components of the same road is ordered sequentially. This means, e.g. in `demo-4.csv`, component `1000000` is connected to component `1000001`, that is connected to component `1000002`, that is connected to component `1000003`, etc., all of which are on road `N1`. Similarity, component `1000013` is connected to component `1000014`, that is connected to component `1000015`, etc., all of which are on road `N2`. Each model component has a unique id according to which the Mesa model is generated. Note that the same `intersection` component that connect different roads would have the same id.

The column `model_type` is used by the model generation to identify which class of components to be generated. The `model_type` labels used in this column must be consistent with the labels in the `generate_model` routine.

The rest of the information is used to instantiate the components (objects).

All data files contained in this directory are used as demonstration for model generation. They are not based on real data.
