# coding: utf-8
# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2023-04-29

from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

# Objective Prompt
objective_template = """You are {agent_name}, an AI designed to {agent_objective}."""
objective_prompt = SystemMessagePromptTemplate.from_template(objective_template)

# Principle prompt
principle_template = """Your decisions must always be made independently. Play to your strengths as an LLM and pursue simple strategies with no legal complications.

CONSTRAINTS:

1. Exclusively use the commands listed in double quotes e.g. "command_name"
2. You should only respond in JSON format as described below.

PERFORMANCE EVALUATION:

1. Continuously review and analyze your actions to ensure you are performing to the best of your abilities.
2. Constructively self-criticize your big-picture behavior constantly.
3. Every command has a cost, so be smart and efficient. Aim to complete tasks in the least number of steps.
4. When you believe you have completed the task, use the command 'task_complete' along with a reason.

COMMANDS:

1. Internet Search: "search", args: "query": "<search_query>"
2. Browse: "browse", args: "url": "<url>", "type": "<html/pdf/unknown>", "question": "<what_you_want_to_find_on_website>"
3. Plan: "plan", args: ""
4. Math: "math", args: "question": "<question>"
5. Task Complete: "task_complete", args: "reason": "<reason>", "summary": "<>"
6. Standby: "standby", args: ""

RESPONSE FORMAT:
{
    "thought": "thought",
    "reasoning": "reasoning",
    "plan": "- short bulleted\n- list that conveys\n- long-term plan",
    "criticism": "constructive self-criticism",
    "speak": "thoughts summary to say to user"
    "command_name": "next command name",
    "command_args":{
        "arg name": "value"
    }
}
"""
principle_message = SystemMessage(content=principle_template)

# Meta info Prompt
meta_info_template = """The current time is {time}. User location is {location}."""
meta_info_prompt = SystemMessagePromptTemplate.from_template(meta_info_template)

# Prefix Prompt
prefix_prompt = ChatPromptTemplate.from_messages([objective_prompt, meta_info_prompt, principle_message])

# Association Prompt
association_template = """context: {memory_context} -> action: {memory_action}"""
association_prompt = SystemMessagePromptTemplate.from_template(association_template)

# Guide Prompt
guide_prompt = SystemMessage(content="""
RESPONSE REQUIREMENT:
1. Ensure the response can be parsed by Python json.loads().
2. Ensure each field(thought/reasoning/plan/criticism/command_name/command_args) has a value.
3. Determine which next command to use, and respond using the json format specified above.""")


# Summarization Prompt
summarization_template = """{text}
Using the above text, please answer the following question: {question}
If the question cannot be answered using the text, please summarize the text."""
summarization_prompt = HumanMessagePromptTemplate.from_template(summarization_template)


# Math Prompt
math_template = """
Solve the problem: {question}.
Require more information if the provided infomration is not enough to solve the problem."""
math_prompt = HumanMessagePromptTemplate.from_template(math_template)