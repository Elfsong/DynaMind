# coding: utf-8
# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2023-04-29

import json
import utils
import prompt
from tqdm import tqdm
from enum import Enum
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.utilities import BingSearchAPIWrapper
from langchain.text_splitter import TokenTextSplitter
from langchain.document_loaders import PlaywrightURLLoader


class TaskType(Enum):
    STANDBY = "stand_by"
    COMPLETE = "task_complete"
    PLAN = "plan"
    SEARCH = "search"
    BROWSE = "browse"
    MESSAGE = "message"
    SUMMARY = "summary"
    MATH = "math"
    UNKNOWN = "unknown"
 
class Task(object):
    def __init__(self, name, args) -> None:
        self.name = name
        self.args = args
        self.task_type = TaskType.UNKNOWN

        # LLM settings
        self.smart_llm = ChatOpenAI(model_name = "gpt-4", temperature=0)
        self.fast_llm = ChatOpenAI(model_name = "gpt-3.5-turbo", temperature=0)
        self.smart_llm_token_limit = 4000
        self.fast_llm_token_limit = 8000
    
    def execute(self):
        raise NotImplementedError("Don't call the base interface.")
    
    def post_process(self, result):
        raise NotImplementedError("Don't call the base interface.")
    
class StandbyTask(Task):
    def __init__(self, name, args) -> None:
        super().__init__(name, args)
        self.task_type = TaskType.STANDBY

    def execute(self):
        pass

class CompleteTask(Task):
    def __init__(self, name, args) -> None:
        super().__init__(name, args)
        self.task_type = TaskType.COMPLETE

    def execute(self):
        return self.args
    
class MathTask(Task):
    def __init__(self, name, args) -> None:
        super().__init__(name, args)
        self.task_type = TaskType.MATH
        self.question = self.args["question"]
        self.llm = self.smart_llm

    def execute(self):
        math_messages = prompt.math_prompt.format_messages(question=self.question)

        # TODO(mingzhe): Token limitation

        # Inference
        with get_openai_callback() as cb:
            result = self.llm(math_messages)
            print(cb)

        return result.content

class SearchTask(Task):
    def __init__(self, name, args) -> None:
        super().__init__(name, args)
        self.task_type = TaskType.SEARCH
        self.query = self.args["query"]
        self.top_k = 5 # TODO(mignzhe): config
        self.search_engine = BingSearchAPIWrapper()

    def execute(self):
        candidates = self.search_engine.results(self.query, self.top_k)
        return candidates
    
class BrowseTask(Task):
    def __init__(self, name, args) -> None:
        super().__init__(name, args)
        self.task_type = TaskType.BROWSE
        self.file_type = self.args["type"]
        self.file_path = self.args["url"]
        self.question = self.args["question"]
        self.fast_model = True
        self.llm = self.fast_llm if self.fast_model else self.smart_llm
    
    def recursive_summary(self, raw_text):
        while self.llm.get_num_tokens(raw_text) > 2000:
            text_splitter = TokenTextSplitter(chunk_size=2000, chunk_overlap=500)
            texts = text_splitter.split_text(raw_text)
        
            summarization_list = list()
            for text in tqdm(texts):
                summarization = SummaryTask("summary", {
                    "text": text,
                    "question": self.question,
                    "fast_model": self.fast_model
                })
                summarization_list += [summarization]
            raw_text = " ".join(summarization_list)

        return raw_text

    def execute(self):
        if self.file_type == "html":
            loader = PlaywrightURLLoader(urls=[self.file_path], remove_selectors=["header", "footer"])
        raw_data = loader.load()

        result = self.recursive_summary(raw_data[0].page_content)

        return result 
        
class SummaryTask(Task):
    def __init__(self, name, args) -> None:
        super().__init__(name, args)
        self.task_type = TaskType.SUMMARY
        self.text = self.args["text"]
        self.question = self.args["question"]

        # Model Selection
        self.llm = self.fast_llm if self.args["fast_model"] else self.smart_llm
        self.token_quota = self.fast_llm_token_limit if self.args["fast_model"] else self.smart_llm_token_limit

    def execute(self):
        summary_messages = prompt.summarization_prompt.format_messages(text=self.text, question=self.question)

        # TODO(mingzhe): Token limitation

        # Inference
        with get_openai_callback() as cb:
            result = self.llm(summary_messages)
            print(cb)

        return result.content
        
class PLANTask(Task):
    def __init__(self, name, args) -> None:
        super().__init__(name, args)
        self.task_type = TaskType.PLAN

        # Model Selection
        self.llm = self.fast_llm if self.args["fast_model"] else self.smart_llm
        self.token_quota = self.fast_llm_token_limit if self.args["fast_model"] else self.smart_llm_token_limit
    
    def execute(self):
        # Prefix Prompt
        prefix_messages = self.args["prefix_messages"]
        self.token_quota -= self.llm.get_num_tokens_from_messages(prefix_messages)

        # Retrieve memory
        # TODO(mingzhe): follow short term memory
        long_term_association = self.args["long_term_memory"]
        
        # Short-term Memory
        short_term_list = self.args["short_term_memory"]
        short_term_messages = list()
        short_term_quota = 2000
        while short_term_list:
            short_term_messages += [short_term_list.pop()]
            short_term_messages_count = self.llm.get_num_tokens_from_messages(short_term_messages)
            if short_term_quota - short_term_messages_count< 0:
                short_term_messages.pop()
                break

        # History
        history_list = self.args["history"]
        history_messages = list()
        history_quota = min(1200, self.token_quota - 2000)

        while history_list:
            history_messages += [history_list.pop()]
            history_messages_count = self.llm.get_num_tokens_from_messages(history_messages)
            if history_quota - history_messages_count < 0:
                history_messages.pop()
                break
        history_messages.reverse()

        guide_messages = [prompt.guide_prompt]

        print(short_term_messages)

        print(history_messages)

        # Inference
        with get_openai_callback() as cb:
            result = self.llm(prefix_messages + short_term_messages + history_messages + guide_messages)
            print(cb)
        return utils.response_parse(result.content)