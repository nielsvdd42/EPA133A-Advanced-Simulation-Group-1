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
scenarios = [{'A': 0.00, 'B': 0.00, 'C':0.00, 'D':0.00},
             {'A': 0.00, 'B': 0.00, 'C':0.00, 'D':0.05},
            {'A': 0.00, 'B': 0.00, 'C':0.05, 'D':0.10},
             {'A': 0.00, 'B': 0.05, 'C':0.10, 'D':0.20},
             {'A': 0.05, 'B': 0.10, 'C':0.20, 'D':0.40}]

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
    scenario_result.to_csv(f"../experiment/average_driving_times_scenario{scenario_i}.csv", index_label='Seed')
    scenario_i = scenario_i + 1