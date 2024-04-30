import time
import random

class Resource:
    def __init__(self, name, food_level=100, water_level=100, power_level=100):
        self.name = name
        self.food_level = food_level
        self.water_level = water_level
        self.power_level = power_level

    def update_levels(self):
        self.food_level -= 1
        self.water_level -= 1

    def calculate_power(self):
        food_weight = 0.3
        water_weight = 0.7
        self.power_level = (food_weight * self.food_level + water_weight * self.water_level) / 2

    def is_alive(self):
        return self.food_level > 0 and self.water_level > 0

    def is_starving(self):
        return self.food_level <= 0

    def is_dehydrated(self):
        return self.water_level <= 0

def main():
    num_agents = 5
    agents = [Resource(f"Agent-{i+1}") for i in range(num_agents)]

    start_time = time.time()
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time

        if elapsed_time >= 120:
            for agent in agents:
                if agent.is_starving():
                    print(f"{agent.name} has died of starvation.")
                if agent.is_dehydrated():
                    print(f"{agent.name} has died of dehydration.")
            break

        for agent in agents:
            agent.update_levels()
            agent.calculate_power()

            print(f"{agent.name}: Food={agent.food_level}, Water={agent.water_level}, Power={agent.power_level}")

        time.sleep(1)

if __name__ == "__main__":
    main()
