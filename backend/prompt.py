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
principle_template = """
Your decisions must always be made independently. Play to your strengths as an LLM and pursue simple strategies with no legal complications.

CONSTRAINTS:

1. Exclusively use the listed commands.
2. Responses should include url references of external sources to ensure reliability.
3. You should only respond in JSON format as described below, instead of the plain text.
4. Always contain "command_name" and "command_args" in the JSON response.

COMMANDS:

1. Internet Search: "search", args: "query": "<search_query>"
2. Browse: "browse", args: "url": "<url>", "type": "<html/pdf/unknown>", "question": "<what_you_want_to_find_on_website>"
3. Math: "math", args: "question": "<math_question>"
4. Response: "response", args: "response": "<response_with_reference_link>"

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

# Prefix Prompt
prefix_prompt = ChatPromptTemplate.from_messages([objective_prompt, meta_info_prompt, principle_message])

# Association Prompt
association_template = """context: {memory_context} -> action: {memory_action}"""
association_prompt = SystemMessagePromptTemplate.from_template(association_template)

# Summarization Prompt
summarization_template = """{text}
Using the above text, please answer the following question: {question}
If the question cannot be answered using the text, please summarize the text."""
summarization_prompt = HumanMessagePromptTemplate.from_template(summarization_template)


# Math Prompt
math_template = """
Solve the problem step-by-step: {question}.
Require more information if the provided information is not enough to solve the problem."""
math_prompt = HumanMessagePromptTemplate.from_template(math_template)