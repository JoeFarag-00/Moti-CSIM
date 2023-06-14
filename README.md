# Moti-Based-Culture-Simulation
Adaptive Behavioral Simulation of Creatures In Changing Environments Using Selective Dominance MOGA, Policy Gradients, and A New Form of Culture Algorithm "Moti-Based"


# The Simulation...
We have a island surrounded with the ocean and creatures scattered, and we have 2 seasons, in the summer, food becomes more on the island and less in ocean, [food grows on trees]. In the winter, food becomes more in the ocean but less on the island, those creatures will try to adapt in a manner in which they will make uses of the available amount of food in both seasons as food is there top priority to survive and reproduce. So they will mostly need to go to the ocean and get food in winters, and in summers they will live on land mostly and get food, but there is a catch. 

In summer, if they all stayed on land there will still not be enough food to feed them all, some will have to dive in the ocean and get food, but there are predators in the ocean and the creatures may be hunted down and eaten. In the winter, were food is more in the ocean, if they stayed in the ocean the predators will eat them all. So essentially, they have to establish a strategy of how to manage resources and there goal is to survive and reproduce. 

We could introduce a new class of builder creatures which can cut down food trees and build rafts on the island, this will help them use the raft to travel across the ocean to get food, rafts substantially lowers the chance of the creature being killed by predators, but trees will be less on land due to trees being cut down and deforestaion [1 raft = -1 tree], therefore, even less food on land. Trees could grow back after sometime, but the creatures could die from hunger during this time frame.

# Recap
Creatures: [3 types]
1. Newbies
2. Builders
3. Predators

Season: [2 Types]
1. Summer
2. Winter

Resources: [1 type] 
1. Food

Tools: [2 types]
1. Free diving
2. Raft

# Important Key Elements
1. [1] Raft = [1] tree.
2. [1] Food = [1] Creature.
3. Predator kill rate [40% free diving] and [10% raft] [TBD].
4. Predators kill cooldowns will be made.
5. Creature Life-spans will be based on the food they eat and a maximum of a fixed value.

# Expected Results
1. Simulated Agression and descrimination between Builders and Newbies class.
2. Extinction of Newbies.

# Future Suggested Additions
1. Builders could choose to teach raft building to Newbies and introduce a new form of culture algorithms which I call "Motivation" or Moti-based culture, where the Builders will have total control and choose to sympathize with Newbies, even if it will cost there generations.

# Expected Technologies To Be Used
Backend languges:
1. Python
2. Mojo by Modular
3. C++ OpenCL with ROCm API

# Simulation Enviroment Build:
1. PyGame or Unity [To create the 2D enviroment]




 
