from model import BangladeshModel
import pandas as pd
import numpy as np
"""
    Run simulation
    Print output at terminal
"""

# ---------------------------------------------------------------

# run time 5 x 24 hours; 1 tick 1 minute
run_length = 5 * 24 * 60

# run time 1000 ticks
# run_length = 1000

# seed = 1234567
#
# sim_model = BangladeshModel(seed=seed)
#
# # Check if the seed is set
# print("SEED " + str(sim_model._seed))
#
# # One run with given steps
# for i in range(run_length):
#     sim_model.step()

simulations = 10
#Scenarios
scenarios = [{'w_water': 0.3333, 'w_elevation': 0.3333, 'w_cyclone':0.3334},
             {'w_water': 0.60, 'w_elevation': 0.20, 'w_cyclone':0.20},
             {'w_water': 0.20, 'w_elevation': 0.60, 'w_cyclone':0.20},
             {'w_water': 0.20, 'w_elevation': 0.20, 'w_cyclone':0.60},
             {'w_water': 0.40, 'w_elevation': 0.15, 'w_cyclone':0.45},
             {'w_water': 0.45, 'w_elevation': 0.40, 'w_cyclone':0.15},
             {'w_water': 0.10, 'w_elevation': 0.45, 'w_cyclone':0.45},
             {'w_water': 0.50, 'w_elevation': 0.30, 'w_cyclone':0.20},
             {'w_water': 0.25, 'w_elevation': 0.15, 'w_cyclone':0.60},
             {'w_water': 0.30, 'w_elevation': 0.50, 'w_cyclone':0.20},
             {'w_water': 0.35, 'w_elevation': 0.10, 'w_cyclone':0.55},
             {'w_water': 0.05, 'w_elevation': 0.05, 'w_cyclone':0.90}]

scenario_i = 0
for scenario in scenarios:
    results_hihi = []
    seed = 12
    for i in range(simulations):
        sim_model = BangladeshModel(seed=seed, scenario=scenario)
        # Check if the seed is set
        print("SEED " + str(sim_model._seed))

        # One run with given steps
        for j in range(run_length):
            sim_model.step()
        results_df = sim_model.datacollector.get_model_vars_dataframe()
        results_hihi.append(results_df.iloc[-1].Average_Driving_Time)
        seed = seed + 1
    scenario_result = pd.DataFrame(results_hihi, index=np.arange(12, 22, 1), columns=['Average Driving Time'])
    scenario_result.to_csv(f"../experiment/results_scenario{scenario_i}.csv", index_label='Seed')
    scenario_i = scenario_i + 1