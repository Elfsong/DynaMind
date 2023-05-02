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

        # Memory
        self.short_term_memory = memory.ShortTermMemory()
        self.long_term_memory = memory.LongTermMemory()

        # Current Task
        self.current_task = task.StandbyTask("welcome", {"status": "Waiting for the user feedback."})
        # self.current_task = task.BrowseTask("test",  {'url': 'https://ids.nus.edu.sg/people-researchers.html', 'type': 'html', 'question': 'List of researchers in NUS IDS'})

        # History
        self.history = memory.History()

        # Human Input
        self.human_input = ""
        
    def get_prefix_messages(self):
        self.time = utils.get_current_time()
        self.location = utils.get_current_location("Singapore")
        return prompt.prefix_prompt.format_prompt(agent_name=self.name, agent_objective="/".join(self.personalities), time=self.time, location=self.location).to_messages()
    
    def construct_plan_task(self):
        history_list = self.history.query(top_k=5)
        if history_list:
            last_human_feedback = self.human_input
            # Memory Management
            stm = self.short_term_memory.convert(
                self.short_term_memory.query(last_human_feedback, top_k=5)
            )
            ltm = self.long_term_memory.query(last_human_feedback, top_k=5)
        else:
            stm = None
            ltm = None

        next_task = task.PLANTask("planner", {
            "fast_model": False, 
            "prefix_messages": self.get_prefix_messages(), 
            "history": history_list,
            "long_term_memory": ltm,
            "short_term_memory": stm,
        })
        return next_task
    
    def receive(self, sio, sid, data):
        input = data["command"]
        sio.emit('message', {'content': f"Copy that! Lemme think...", "style": "system"}, room=sid)
        
        if input and self.current_task:
            if input == "y":
                if self.current_task.task_type != task.TaskType.STANDBY:
                    result = self.current_task.execute()

                    # Write result into short-term memory
                    if self.current_task.task_type == task.TaskType.PLAN:
                        print(json.dumps(result, indent=4))

                        self.history.add("ai", result["speak"])
                    
                        # Construct new task by result
                        command_name = result["command_name"]
                        command_args = result["command_args"]

                        # Display Thought
                        sio.emit('message', {'content': f"💭 Thought: {result['thought']}", "style": "thought"}, room=sid)
                        sio.emit('message', {'content': f"🔍 Reasoning: {result['reasoning']}", "style": "reasoning"}, room=sid)
                        sio.emit('message', {'content': f"🗓️ Plan: {result['plan']}", "style": "plan"}, room=sid)
                        sio.emit('message', {'content': f"👨🏼‍⚖️ Criticism: {result['criticism']}", "style": "criticism"}, room=sid)
                        sio.emit('message', {'content': f"🗣️ Speak: {result['speak']}", "style": "speak"}, room=sid)

                        # Generate Next Task
                        if command_name == "task_complete":
                            next_task = task.CompleteTask("complete", command_args)
                        elif command_name == "standby":
                            next_task = task.StandbyTask("welcome", {"status": "Waiting for the user feedback."})
                        elif command_name == "search":
                            next_task = task.SearchTask("search", command_args)
                        elif command_name == "browse":
                            next_task = task.BrowseTask("browse", command_args)
                        else:
                            next_task = task.StandbyTask("welcome", {"status": "Waiting for the user feedback."}) 
                    elif self.current_task.task_type == task.TaskType.COMPLETE:
                        self.short_term_memory.add(key={"command": self.current_task.task_type.value, "args": self.current_task.args}, value=result)
                        next_task = self.construct_plan_task()
                        sio.emit('message', {'content': f"🗣️ Speak: {result['summary']}", "style": "speak"}, room=sid)
                        self.history.add("ai", result["summary"])
                    else:
                        self.short_term_memory.add(key={"command": self.current_task.task_type.value, "args": self.current_task.args}, value=result)
                        next_task = self.construct_plan_task()
                        sio.emit('message', {'content': f"🗂️ Resource: {result}", "style": "resource"}, room=sid)

                    self.current_task = next_task
                else:
                    self.current_task = self.construct_plan_task()
            elif input == "n":
                self.current_task = task.StandbyTask("withdraw", {"status": "Waiting for the user feedback."})
            else:
                self.history.add("user", input)
                self.human_input = input
                self.current_task = self.construct_plan_task()
        else:
            self.current_task = task.StandbyTask("welcome", {"status": "Waiting for the user feedback."})
        
        sio.emit('message', {'content': f"Next Task: {self.current_task.task_type.value}", "style": "system"}, room=sid)
        if self.current_task.task_type != task.TaskType.PLAN:
            sio.emit('message', {'content': f"Args: {self.current_task.args}", "style": "system" }, room=sid)
        sio.emit('message', {'content': f"[Y] to preceed ✅ / [N] to terminate 🛑 / Typing to feedback 💬", "style": "system"}, room=sid)

if __name__ ==  "__main__":
    agent = Agent("CISCO_BOT", ["help customers solving their problems"])

    while True:
        print(f"Command: {agent.current_task.task_type.value}")
        if agent.current_task.task_type != task.TaskType.PLAN:
            print(agent.current_task.args)

        print("[Y] to preceed 🟢 / [N] to terminate 🔴 / typing to feedback 💬")
        agent.receive(input("Command > ").lower().strip())


