# coding: utf-8
# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2023-04-29

import utils
import task
import prompt
import memory
import json

class Agent(object):
    def __init__(self, name, personalities) -> None:
        # Agent Name
        self.name = name

        # Personality
        self.personalities = personalities

        # History
        self.history = memory.History()

        # Memory
        self.short_term_memory = memory.ShortTermMemory()
        self.long_term_memory = memory.LongTermMemory()

        # Current Task
        self.current_task = task.StandbyTask("welcome", {"status": "Waiting for the user input."})

        # Human Input
        self.human_input = ""
        
    def get_prefix_messages(self):
        self.time = utils.get_current_time()
        self.location = utils.get_current_location("Singapore")
        return prompt.prefix_prompt.format_prompt(agent_name=self.name, agent_objective="/".join(self.personalities), time=self.time, location=self.location).to_messages()
    
    def short2long(self):
        pass

    def new_receive(self, sio=None, sid=None, data=None):
        try:
            # Get user_input
            query = data["user_input"]

            # Add user_input into history
            self.history.add("user", query)

            while True:
                planner = task.PLANTask("planner", {
                    "fast_model": False, 
                    "prefix_messages": self.get_prefix_messages(), 
                    "history": self.history.query(top_k=5),
                    "long_term_memory": self.long_term_memory.convert(self.long_term_memory.query(query, top_k=5)),
                    "short_term_memory": self.short_term_memory.convert(self.short_term_memory.query(query, top_k=5)),
                })

                next_task = planner.execute()
                task_name = next_task["command_name"]
                task_args = next_task["command_args"]

                if task_name == "complete":
                    response = task_args['response']
                    sio.emit('message', {'content': f"🗣️ {response}", "style": "speak"}, room=sid)
                    self.history.add("assistant", response)
                    self.short2long()
                    break
                else:
                    if task_name == "search":
                        search_task = task.SearchTask("search", task_args)
                        result = search_task.execute()
                        self.short_term_memory.add(key=f"search: {task_args['query']}", value=result)
                    elif task_name == "browse":
                        browse_task = task.BrowseTask("browse", task_args)
                        result = browse_task.execute()
                        self.short_term_memory.add(key=f"browse: {task_args['url']}-{task_args['question']}", value=result)
                    elif task_name == "math":
                        math_task = task.MathTask("math", task_args)
                        result = math_task.execute()
                        self.short_term_memory.add(key=f"math: {task_args['question']}", value=result)
                    else:
                        pass
                
        except Exception as e:
            print(f"Error: {e}")
            sio.emit('message', {'content': f"System Error: {e}. It's weird, could you retry?", "style": "system"}, room=sid)

if __name__ ==  "__main__":
    agent = Agent("CISCO_BOT", ["help customers solving their problems"])

    while True:
        print(f"Command: {agent.current_task.task_type.value}")
        if agent.current_task.task_type != task.TaskType.PLAN:
            print(agent.current_task.args)

        agent.new_receive(data = {"user_input": input("Command > ").lower().strip()})


