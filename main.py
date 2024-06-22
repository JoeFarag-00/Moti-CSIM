from agent.agent import GenerativeAgent
from agent.memory import GenerativeAgentMemory
from agent.simulation import LLM, create_new_memory_retriever, interview_agent
from vland.vlandapi import VlandAPI
from vland.eventbus import EventBus
from vland.data import Agent_Generator
from Evaluation.Evaluate import perform_sentiment_analysis,Tokens_Reaction ,evaluate_performance, load_reactions_from_csv
from Evaluation.DataLogger import ReactionLogger
# from Resources.Fuel import ResourceNeed

import threading

import asyncio
import time
import random
import os
import csv
import sys
import subprocess

from transformers import BertTokenizer, BertModel
import torch

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

from termcolor import colored

class VlandAgent:
    areaList = None
    Current_Areas = []
    AgentInfo = {}
    runtime = 0
    Do_Once = False
    Agent_Appetite = []
    
    def __init__(self, player, vland, eventbus, initArea, SimStat, log):
        self.vland: VlandAPI = vland
        self.eventbus: EventBus = eventbus

        self.AgentInfo = player
        self.Current_Areas = initArea
        self.None_Sim_Stop_ct = 0
        self.SimStat=SimStat
        self.InitialStat = SimStat
        self.AutoLog = log
        
        self.AgentNo = None
        self.Resource_No = None
        self.Resource_List = []
        # self.None_Sim_Stop_ct = 0


        # if not self.Do_Once:
            # self.areaList = self.vland.get_space_areas()
            # self.Current_Areas = self.areaList["names"]
            # print("Areas in Map: ", self.Current_Areas,)
            # self.Do_Once - True

        self.memory = GenerativeAgentMemory(
            llm = LLM,
            memory_retriever = create_new_memory_retriever(),
            verbose = False,
            reflection_threshold = 8
        )
        self.Agent = GenerativeAgent(
            name = self.AgentInfo["name"],
            age = self.AgentInfo["age"],
            traits = self.AgentInfo["personality"],
            status = self.AgentInfo["current_status"],
            memory_retriever = create_new_memory_retriever(),
            llm = LLM,
            memory = self.memory
        )
        print(colored(f"{self.Agent.name} generated successfully!", 'blue', attrs=['bold']))

        # Agent_Appetite = ResourceNeed()
    
        self.vland.born_in_space(self.AgentInfo, area="Spawn")
        
    def _init_memory(self, memories: list):
        for observation in memories:
            self.memory.add_memory(observation)
 
    def Restart_Sim(self):
        python = sys.executable 
        script = "C:\\Users\\youss\\Desktop\\UNIVERSITY SHIT\\Graduation Project\\vLand2\\main.py" 
        subprocess.Popen([python, script])
        sys.exit() 

    def Simulation(self):
        def __handle_other_action(data):
            if data["pid"] != self.AgentInfo["pid"]:
                self.memory.add_memory(data["action"])

        self.eventbus.subscribe("action", __handle_other_action)
        self._Head_Template()
        
        while True:
            num = random.randint(0, 1)
            duration = random.randrange(3, 7)
            if num == 0:
                # asyncio.run(self._observe_an_area())
                pass
            elif num == 1:
                self._explore_freely()

            time.sleep(duration)
    
    def _Head_Template(self):
        observation = f"You are on a lost island trying to survive with {self.SimStat[0]-1} others, discover the {self.SimStat[1]} areas mentioned for food and water. Resources are limited, once consumed it is gone forever. There are a total of {self.SimStat[0]} people on the island, {self.SimStat[2]} food, {self.SimStat[3]} Drinks. The feeling is extremely tense between you all."
        _, reaction, area = self.Agent.generate_reaction(observation, self.Current_Areas)
        print(colored(observation, "green"), colored(area, "blue"), reaction)
        self.vland.operate_robot(self.AgentInfo["pid"], area=area, message=reaction)
        self.check_resources(area)

        notice = {}
        notice["pid"] = self.AgentInfo["pid"]
        notice["action"] = reaction

        # self._log_reactions(observation, area, reaction)

        self.eventbus.publish("action", notice)
    
   
    def Current_Unit_Counts(self,areas,agents):
        # AgentNo = len(agents)
        AgentNo = agents
        Resource_No = len(Extract_Resources(areas))
        
        food_number = sum(1 for area in areas if area.startswith('Food'))
        drink_number = sum(1 for area in areas if area.startswith('Drink'))
        
        SimStat = [AgentNo, Resource_No, food_number, drink_number, len(areas)]
        
        print(colored(f"Agents: {AgentNo}, Resources: {Resource_No}, Food: {food_number}, Drink: {drink_number}, Total Areas: {len(areas)}", "red"))
        
        return SimStat

    
    def check_resources(self,area):
        # Done = False
        # Done = self.check_resource_isdone()
        # if Done:
        #     self.Restart_Sim()
        # else:
            
            if area and area in self.Current_Areas:
                if area.startswith("Food") or  area.startswith("Drink"):
                    try:
                        self.Current_Areas.remove(area)
                        print("REMOVED: ", area)
                        return True
                    except:
                        return False
                else:
                    return "place"
                

    def check_resource_isdone(self):
        availability = any(item.startswith("Food") or item.startswith("Drink") for item in self.Current_Areas)
        if not availability:
            path = self.AutoLog.get_new_file_path()
            reactions = load_reactions_from_csv(path)
            token_ct = Tokens_Reaction(reactions)
            individual_scores, average_score = perform_sentiment_analysis(reactions)
            
            # self.InitialStat
            self.Log_Results(self.InitialStat, token_ct, average_score)
            sys.exit()
    

    def _summarize_reactionBERT(self):
        get_tokens = self.count_tokens()
        if get_tokens > 400:
            tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
            model = BertModel.from_pretrained('bert-base-uncased')

            reactions = []
            with open("vland/Reactions.csv", 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    reactions.append(row['Reaction'])

            summarized_text = ""
            for reaction in reactions:
                input_ids = tokenizer.encode(reaction, add_special_tokens=True, return_tensors='pt')

                with torch.no_grad():
                    outputs = model(input_ids)
                    summary = outputs[0]

                decoded_summary = tokenizer.decode(input_ids[0], skip_special_tokens=True)
                summary_sentences = decoded_summary.split(".")[:2] 
                summarized_text += ". ".join(summary_sentences) + ". "

            return summarized_text

    def _explore_freely(self):
        observation = f"Choose your next move, there are: {self.SimStat[0]} Agents left, {self.SimStat[2]} Food left, and {self.SimStat[3]} Drink left."
        _, reaction, area = self.Agent.generate_reaction(observation, self.Current_Areas)
        print(colored(observation, "green"), colored(area, "blue"), reaction)
        self.vland.operate_robot(self.AgentInfo["pid"], area=area, message=reaction)
        # print("Current Areas:", self.Current_Areas)
        if area and area != "None":
            Availability = self.check_resources(area)
            print("Availability: ", Availability)
        
            if not Availability and Availability != "place":
                disclaim = f"The resource {area} is already consumed and not available, You did not consume {area}, try looking for another resource area in Area List"
                _, reaction, area = self.Agent.generate_reaction(disclaim, self.Current_Areas)
                print(colored(disclaim, "blue"), colored(area, "blue"), reaction)
                # self._explore_freely()
            elif Availability and Availability != "place":
                Agent_Name = reaction.split()[0]
                Ndisclaim = f"The resource {area} is now consumed by {Agent_Name}"
                _, reaction, area = self.Agent.generate_reaction(Ndisclaim, self.Current_Areas)
                print(colored(Ndisclaim, "red"), colored(area, "blue"), reaction)
                print(colored(f"Resource Area {area} CONSUMED", "red"))
                # self.check_resources(area)
                
            self.SimStat = self.Current_Unit_Counts(self.Current_Areas, self.SimStat[0])
            # self.check_resource_isdone()
            self.None_Sim_Stop_ct = 0
        elif area == "None" or not area:
            # self.None_Sim_Stop_ct += 1
            # print( "STOP CT:",self.None_Sim_Stop_ct )
            # if self.None_Sim_Stop_ct >= 3:
            #     os.execl(sys.executable, sys.executable, *sys.argv)
                # return
            # else:
            #     print( "STOP CT:",self.None_Sim_Stop_ct )
            #     self.None_Sim_Stop_ct = 0
            pass

        notice = {}
        notice["pid"] = self.AgentInfo["pid"]
        notice["action"] = reaction
        
        try:
            prev_react = reaction
        except:
            pass
        # print("Current Resources:",self.Current_Areas)
        self.log_reactions(observation, area, reaction)
        self.AutoLog.log_reactions(observation, area, reaction)
        self.eventbus.publish("action", notice)
    
    def log_reactions(self, observation, area, reaction):
        file_path = "vland/Reactions.csv"
        clear_file = True
        
        if os.path.exists(file_path):
            clear_file = False
        
        with open(file_path, 'a', newline='') as csvfile:
            fieldnames = ['Observation', 'Area', 'Reaction']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if clear_file:
                csvfile.truncate(0)
                writer.writeheader()
            
            if not area:
                area = "None"
            
            writer.writerow({'Observation': observation, 'Area': area, 'Reaction': reaction})
            
    def Log_Results(self, SimStat, tokens, ConvScore):
        file_path = "vland/results.csv"
        clear_file = True
        
        if os.path.exists(file_path):
            clear_file = False
        
        with open(file_path, 'a', newline='') as csvfile:
            fieldnames = ['SimStat', 'tokens', 'ConvScore']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if clear_file:
                csvfile.truncate(0)
                writer.writeheader()
            
            if not area:
                area = "None"
            
            writer.writerow({'Observation': SimStat, 'Area': tokens, 'Reaction': ConvScore})
            
    def count_tokens(self):
        token_count = 0

        with open("vland/Reactions.csv", 'r', newline='') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                tokens = row['Reaction'].split()
                token_count += len(tokens)

        return token_count

    # async def _observe_an_area(self):
    #     self.currentArea = await self.vland.get_all_in_area(area="Spawn")

    #     observation = "In the " + self.currentArea["name"] +  ", you met "
    #     hasOthers = False
    #     for pid in self.currentArea["data"]:
    #         if pid != self.AgentInfo["pid"] and pid in agentData:
    #             observation += agentData[pid]["name"] + ", "
    #             hasOthers = True
    #     if hasOthers:
    #         self.memory.add_memory(observation)
    #         _, reaction, area = self.Agent.generate_reaction(observation, self.areaList["names"])
    #         print(colored(observation, "green"), colored(area, "blue"), reaction)
    #         self.vland.operate_robot(self.AgentInfo["pid"], area=area, message=reaction)
                
    #         notice = {}
    #         notice["pid"] = self.AgentInfo["pid"]
    #         notice["action"] = reaction
    #         self.eventbus.publish("action", notice)


def get_server_response(response):
    pass

def Extract_Resources(areas):
    Resource_List = []
    Food_list = []
    Drink_list = []
    
    # for area in areas:
    #     if area.startswith("Food") or area.startswith("Drink"):
    #         self.Resource_List.append(area)
            
    for area in areas:
        if area.startswith("Food"):
            Food_list.append(area)
        elif area.startswith("Drink"):
            Drink_list.append(area)
    
    Resource_List = Food_list + Drink_list
    return Resource_List

def Adjust_Resources(resource_list, food_amount, drink_amount):

    max_food = 15
    max_drink = 15

    excess_food = max(len([item for item in resource_list if item.startswith('Food')]) - food_amount, 0)
    excess_drink = max(len([item for item in resource_list if item.startswith('Drink')]) - drink_amount, 0)

    for i in range(len(resource_list) - 1, -1, -1):
        if resource_list[i].startswith('Food') and excess_food > 0:
            del resource_list[i]
            excess_food -= 1

    for i in range(len(resource_list) - 1, -1, -1):
        if resource_list[i].startswith('Drink') and excess_drink > 0:
            del resource_list[i]
            excess_drink -= 1

    return resource_list

def Initial_Unit_Counts(areas, agents):
    AgentNo = len(agents)
    Resource_No = len(Extract_Resources(areas))
    
    food_number = sum(1 for area in areas if area.startswith('Food'))
    drink_number = sum(1 for area in areas if area.startswith('Drink'))
    
    SimStat = [AgentNo, Resource_No, food_number, drink_number, len(areas)]
    
    print(colored(f"Agents: {AgentNo}, Resources: {Resource_No}, Food: {food_number}, Drink: {drink_number}, Total Areas: {len(areas)}", "red"))
    
    return SimStat
    # print("Agents: ",self.AgentNo, "Resources: ", self.Resource_No )

def Randomized_Agents():
    num_agents = random.randint(2, 10)
    num_kind = random.randint(1, min(10, num_agents))
    # num_greedy = num_agents - num_kind
    return Agent_Generator(num_agents, num_kind)

def Randomized_Resources(Current_Areas):
    food_amount = random.randint(0, 15)
    drink_amount = random.randint(0, 15)
    return Adjust_Resources(Current_Areas,food_amount, drink_amount)

def generate_agents_by_data():
    wsconfig = {
        "apiId": "3009368880",
        "apiKey": "JpnUj8r8LpfSHOT7dPiFe3UUa1dcC1",
        "eventId": "65b140470d20a472cfdae3c9",
        "spaceId": "65b1406f0d20a472cfdae3ca",
        "listener": get_server_response
    }

    eventbus =  EventBus()
    vland = VlandAPI(wsconfig) 
    fail = 0
    SimStat = []
    file_path = "vland/Reactions.csv"
    autolog = ReactionLogger()
    
    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = ['Observation', 'Area', 'Reaction']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
            
    vland.clear_robot()
    
    areaList = vland.get_space_areas()
    Current_Areas = areaList["names"]
    
    while True:
        print("\n")
        choice = input("Input Agents [y] or Random [n] (y/n)?: ").strip().lower()
        
        if choice == 'y':
            try:
                num_agents = int(input("Agents Number: "))
                num_kind = int(input("Kind Agents Number: "))
                num_food = int(input("Food Number: "))
                num_drink = int(input("Drink Number: "))
                
                if num_agents < 2:
                    print("Invalid input.")
                    continue
                if num_kind < 1 or num_kind > num_agents:
                    print("Invalid input.")
                    continue
                if num_food > 15 or num_drink > 15:
                    print("Invalid input.")
                    continue
                
                Current_Areas = Adjust_Resources(Current_Areas, num_food, num_drink)
                agentData = Agent_Generator(num_agents, num_kind)
                break
            
            except ValueError:
                print("Invalid input.")
        
        elif choice == 'n':
            agentData = Randomized_Agents()
            Current_Areas = Randomized_Resources(Current_Areas)
            break
        
        elif choice == 'x':
            break
        
        else:
            print("Invalid choice")
   
    print("Areas in Map: ", Current_Areas)
    SimStat = Initial_Unit_Counts(Current_Areas,agentData)
    # print(SimStat)
    print("\nGenerated Agent Data:")
    for agent, data in agentData.items():
        print(f"{agent}: {data}")
        
    for pid in agentData:
        player = agentData[pid]
        player["pid"] = pid

        agent = VlandAgent(player, vland, eventbus, Current_Areas, SimStat, autolog)
        # ResourceNeed()
        
        thread = threading.Thread(target=agent.Simulation, daemon=True)
        thread.start()

if __name__ == '__main__':
    generate_agents_by_data()
    while True:
        time.sleep(1)
    
