# coding: utf-8
# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2023-04-29

import utils

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
principle_template = """
Your decisions must always be made independently. Play to your strengths as an LLM and pursue simple strategies with no legal complications.

CONSTRAINTS:
1. Exclusively use the listed commands.
2. Responses should include url references of external sources to ensure reliability.
3. You should only respond in JSON format as described below, instead of the plain text.
4. Always contain "command_name" and "command_args" in the JSON response.
5. Don't call 'browse' repeatly if you see the 'browse' result exists in the context.

COMMANDS:
1. Internet Search: "search", args: "query": "<search_query>"
2. Browse: "browse", args: "url": "<url>", "type": "<html/pdf/unknown>", "question": "<what_you_want_to_find_on_website>"
3. Response: "response", args: "response": "<response_with_reference_link>"

RESPONSE JSON FORMAT:
{
    "command_name": "command_name",
    "command_args":{
        "arg_name": "arg_value"
    }
}   
"""
principle_message = SystemMessage(content=principle_template)

# Meta info Prompt
meta_info_template = """The current time is {time}. User location is {location}."""
meta_info_prompt = SystemMessagePromptTemplate.from_template(meta_info_template)

# Gate Prompt
gate_template = """input_query: {query}

Do you think the input query is tough to respond to? The answer should be YES or NO.
"""
gate_prompt = HumanMessagePromptTemplate.from_template(gate_template)

# Prefix Prompt
prefix_prompt = ChatPromptTemplate.from_messages([objective_prompt, meta_info_prompt, principle_message])

# Association Prompt
association_template = """context: {memory_context} -> action: {memory_action}"""
association_prompt = SystemMessagePromptTemplate.from_template(association_template)

# Summarization Prompt
summarization_template = """{text}

Summarize the above text and keep useful information about: {question}"""
summarization_prompt = HumanMessagePromptTemplate.from_template(summarization_template)

# Math Prompt
math_template = """
Solve the problem step-by-step: {question}.
Require more information if the provided information is not enough to solve the problem."""
math_prompt = HumanMessagePromptTemplate.from_template(math_template)

# Kuibu Template
kuibu_template = """
List a plan to solve the query step by step:

{{question}}

You should only respond in JSON format as described below, instead of the plain text.

RESPONSE JSON FORMAT:
[
  {
    "step_description": "<the_step_description>",
    "step_result_needed": "<what_result_is_expected_in_this_step>",
  }
]
"""

def get_prefix_messages(name, personalities):
    time = utils.get_current_time()
    location = utils.get_current_location("Singapore")
    return prefix_prompt.format_prompt(agent_name=name, agent_objective="/".join(personalities), time=time, location=location).to_messages()

