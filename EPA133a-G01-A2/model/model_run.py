from model import BangladeshModel
"""
    Run simulation
    Print output at terminal
"""

# ---------------------------------------------------------------

# run time 5 x 24 hours; 1 tick 1 minute
run_length = 5 * 24 * 60

# run time 1000 ticks
# run_length = 1000

seed = 12
simulations = 10
scenario1 = {'A': 0, 'B': 0, 'C':0, 'D':0.05}


for i in range(simulations):
    sim_model = BangladeshModel(seed=seed, scenario=scenario1)

    # Check if the seed is set
    print("SEED " + str(sim_model._seed))

    # One run with given steps
    for i in range(run_length):
        sim_model.step()

    results_df = sim_model.datacollector.get_model_vars_dataframe()

    results_df.to_csv(f"../experiment/average_driving_times_seed{seed}_scenario1_real.csv", index_label='Step')
    seed = seed + 1
    print("Simulation complete. Data saved to 'average_driving_times.csv'.")