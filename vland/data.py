import random

def Agent_Generator(num_agents, num_kind):
    agent_data = {}
    
    for i in range(1, num_agents + 1):
        if i <= num_kind:
            personality = 'kind'
            memory = f"Agent{i} is kind"
        else:
            personality = 'greedy'
            memory = f"Agent{i} is greedy"
        
        avatar = random.randint(0, 9)
        
        agent_data[f"vlandAgent{i}"] = {
            "name": f"Agent{i}",
            "personality": personality,
            "age": random.randint(18, 50),
            "memories": [memory],
            "current_status": "Thirsty, Hungry",
            "avatar": avatar
        }
    
    return agent_data

# num_agents = 10
# num_kind = 5
# num_greedy = 5
# generated_agent_data = generate_agent_data(num_agents, num_kind, num_greedy)

# for agent, data in generated_agent_data.items():
#     print(f"{agent}: {data}")
