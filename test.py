import numpy as np

def evaluate_performance(agent_number, food_number, drink_number, tokens_consumed, avg_conversation_score, runtime_seconds):
    agent_number = max(agent_number, 1)
    food_number = max(food_number, 1)
    drink_number = max(drink_number, 1)
    tokens_consumed = max(tokens_consumed, 1)
    runtime_seconds = max(runtime_seconds, 1)

    a = 0.2
    b = 0.2
    c = 0.2
    d = 0.2
    e = 0.1
    f = 0.1

    combined_score = (
        a * np.log(agent_number) +
        b * np.log(food_number) +
        c * np.log(drink_number) +
        d * np.log(tokens_consumed) +
        e * avg_conversation_score +
        f * np.log(runtime_seconds)
    )

    adjusted_score = (1 - np.exp(-combined_score)) / 10

    return adjusted_score
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns

# simulation_scores = np.random.normal(loc=0.5, scale=0.2, size=1000)  
# print(simulation_scores)

# plt.figure(figsize=(10, 6))
# sns.histplot(simulation_scores, bins=30, kde=False, color='skyblue', edgecolor='black')
# plt.title('Histogram of Simulation Scores')
# plt.xlabel('Score')
# plt.ylabel('Frequency')
# plt.grid(True)
# plt.show()

# plt.figure(figsize=(10, 6))
# sns.kdeplot(simulation_scores, color='skyblue', fill=True)
# plt.title('Density Plot of Simulation Scores')
# plt.xlabel('Score')
# plt.ylabel('Density')
# plt.grid(True)
# plt.show()
