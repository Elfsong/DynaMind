# coding: utf-8
# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2023-04-29

import utils
import task
import prompt
import memory

class Agent(object):
    def __init__(self, name, personalities) -> None:
        # Agent Name
        self.name = name

        # Personality
        self.personalities = personalities

        # History
        self.history = memory.History()

        # Action History
        self.action_history = memory.History()

        # Memory
        self.short_term_memory = memory.ShortTermMemory()
        self.long_term_memory = memory.LongTermMemory()

        # Current Task
        self.current_task = task.StandbyTask("welcome", {"status": "Waiting for the user input."})

        # Human Input
        self.human_input = ""

        # Credit
        self.credit = 0
    
    def short2long(self, query, response, lt_candidates):
        # Save <query, answer> pair
        self.long_term_memory.add([utils.get_history_str(self.history.query(top_k=5))], [response])

        for doc in self.short_term_memory.query(query, top_k=5):
            doc_uuid = doc.metadata["uuid"]
            doc_key = doc.metadata["key"]
            doc_content = doc.page_content

            if doc_uuid in lt_candidates:
                # TODO(mingzhe): Check if adding into long-term memory

                # Similarity Check
                if self.long_term_memory.query(doc_key, top_k=5, threshold=0.1):
                    print("Alreay has the item. Skipped.")
                else:
                    self.long_term_memory.add([doc_key], [doc_content])

    def receive(self, query, socket_config):
        sio, sid = socket_config

        # Add user_input into history
        self.history.add("user", query)

        # Long-term memory candidates (UUID)
        lt_candidates = set()

        self.credit = 5
        self.action_history.clear()

        while self.credit:
            self.credit -= 1

            planner = task.PLANTask("planner", {
                "fast_model": False, 
                "prefix_messages": prompt.get_prefix_messages(self.name, self.personalities), 
                "query": query,
                "history": self.history.query(top_k=5),
                "action_history": self.action_history.query(top_k=5),
                "long_term_memory": self.long_term_memory.convert(self.long_term_memory.query(query, top_k=5, threshold=0.3)),
                "short_term_memory": self.short_term_memory.convert_with_meta(self.short_term_memory.query(query, top_k=5)),
            })
            sio.emit('message', {'content': f"🔮 Thinking: {query}", "style": "system"}, room=sid)
            next_task, short_term_uuids = planner.execute()
            lt_candidates.update(short_term_uuids)

            try:
                task_name = next_task["command_name"]
                task_args = next_task["command_args"]
            except Exception as e:
                self.history.add("assistant", str(next_task))
                sio.emit('message', {'content': f"🗣️ {next_task}", "style": "speak"}, room=sid)
                break

            if task_name == "response":
                response = task_args['response']
                sio.emit('message', {'content': f"🗣️ {response}", "style": "speak"}, room=sid)
                self.history.add("assistant", response)
                sio.emit('message', {'content': f"🧠 Moving short-term memory to long-term memory...", "style": "system"}, room=sid)
                self.short2long(query, response, lt_candidates)
                break
            else:
                sio.emit('message', {'content': f"Action: {task_name}, Args: {task_args}", "style": "task"}, room=sid)
                
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

                self.action_history.add("assistant", f"command_name: {task_name} command_args: {task_args} has been tried. Don't use this same command again.")

    def execute(self, query):
        # Add user_input into history
        self.history.add("user", query)

        # Long-term memory candidates (UUID)
        lt_candidates = set()

        self.credit = 5
        self.action_history.clear()

        while self.credit:
            self.credit -= 1

            planner = task.PLANTask("planner", {
                "fast_model": False, 
                "prefix_messages": prompt.get_prefix_messages(self.name, self.personalities), 
                "query": query,
                "history": self.history.query(top_k=5),
                "action_history": self.action_history.query(top_k=5),
                "long_term_memory": self.long_term_memory.convert(self.long_term_memory.query(query, top_k=5, threshold=0.3)),
                "short_term_memory": self.short_term_memory.convert_with_meta(self.short_term_memory.query(query, top_k=5)),
            })
    
            next_task, short_term_uuids = planner.execute()
            lt_candidates.update(short_term_uuids)

            try:
                task_name = next_task["command_name"]
                task_args = next_task["command_args"]
            except Exception as e:
                self.history.add("assistant", str(next_task))
                return str(next_task)

            if task_name == "response":
                response = task_args['response']
                self.history.add("assistant", response)
                self.short2long(query, response, lt_candidates)
                return response
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

                self.action_history.add("assistant", f"command_name: {task_name} command_args: {task_args} has been tried. Don't use this same command again.")
        return "Sorry, I can't respend to it."     

if __name__ ==  "__main__":
    agent = Agent("CISCO_BOT", ["help customers solving their problems"])

    while True:
        agent.receive(data = {"user_input": input("Command > ").lower().strip()})


