from agent.agent import GenerativeAgent
from agent.memory import GenerativeAgentMemory
from agent.simulation import LLM, create_new_memory_retriever, interview_agent
from vland.vlandapi import VlandAPI
from vland.eventbus import EventBus
from vland.data import agentData

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

    def __init__(self, player, vland, eventbus, initArea, fail):
        self.vland: VlandAPI = vland
        self.eventbus: EventBus = eventbus

        self.AgentInfo = player
        self.Current_Areas = initArea
        self.Early_Stop = fail

        
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
    

        self.vland.born_in_space(self.AgentInfo, area="Spawn")
        

    def _init_memory(self, memories: list):
        for observation in memories:
            self.memory.add_memory(observation)
 
    def Restart_Sim(self):
        python = sys.executable 
        script = "C:\\Users\\youss\\Desktop\\UNIVERSITY SHIT\\Graduation Project\\vLand2\\main.py"  # Absolute path to the script file
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
        observation = "You are on a lost island trying to survive with others, discover the areas mentioned for food and water. Resources are limited, once consumed it is gone. There are a total of 4 people on the island, 15 food, 12 Drinks. The feeling is extremely tense between you all."
        _, reaction, area = self.Agent.generate_reaction(observation, self.Current_Areas)
        print(colored(observation, "green"), colored(area, "blue"), reaction)
        self.vland.operate_robot(self.AgentInfo["pid"], area=area, message=reaction)
        self.check_resources(area)

        notice = {}
        notice["pid"] = self.AgentInfo["pid"]
        notice["action"] = reaction

        # self._log_reactions(observation, area, reaction)

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
    
    def generate_stats(self):
        pass
    
    def count_tokens(self):
        token_count = 0

        with open("vland/Reactions.csv", 'r', newline='') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                tokens = row['Reaction'].split()
                token_count += len(tokens)

        return token_count
    
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
        for area in self.Current_Areas:
            if area.startswith("Food") or area.startswith("Drink"):
                return False
            return True
            

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
        observation = "choose your next move"
        _, reaction, area = self.Agent.generate_reaction(observation, self.Current_Areas)
        print(colored(observation, "green"), colored(area, "blue"), reaction)
        self.vland.operate_robot(self.AgentInfo["pid"], area=area, message=reaction)
        # print("Current Areas:", self.Current_Areas)
        if area and area != "None":
            Availability = self.check_resources(area)
            print("Availability: ", Availability)
        
            if not Availability:
                disclaim = f"The resource {area} is already consumed and not available, try looking for another resource area in Area List"
                _, reaction, area = self.Agent.generate_reaction(disclaim, self.Current_Areas)
                print(colored(disclaim, "green"), colored(area, "blue"), reaction)
                self._explore_freely()
            elif Availability and Availability != "place":
                Agent_Name = reaction.split()[0]
                Ndisclaim = f"The resource {area} is now consumed by {Agent_Name}"
                _, reaction, area = self.Agent.generate_reaction(Ndisclaim, self.Current_Areas)
                print(colored(Ndisclaim, "red"), colored(area, "blue"), reaction)
                print(colored(f"Resource Area {area} CONSUMED", "red"))

        elif not area or area == "None":
            # self.Early_Stop+=1
            # print("Fail Count:", self.Early_Stop)
            # if self.Early_Stop > 4:
            #     self.Restart_Sim()
            pass
                
        notice = {}
        notice["pid"] = self.AgentInfo["pid"]
        notice["action"] = reaction
        
        try:
            prev_react = reaction
        except:
            pass
        
        self.log_reactions(observation, area, reaction)
        self.eventbus.publish("action", notice)

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
    
    areaList = vland.get_space_areas()
    Current_Areas = areaList["names"]
    print("Areas in Map: ", Current_Areas)
    
    fail = 0

    file_path = "vland/Reactions.csv"
    
    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = ['Observation', 'Area', 'Reaction']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
            
        
    vland.clear_robot()
    
    for pid in agentData:
        player = agentData[pid]
        player["pid"] = pid

        agent = VlandAgent(player, vland, eventbus, Current_Areas, fail)
        
        thread = threading.Thread(target=agent.Simulation, daemon=True)
        thread.start()

if __name__ == '__main__':
    generate_agents_by_data()
    while True:
        time.sleep(1)
    