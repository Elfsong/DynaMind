# coding: utf-8
# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2023-04-29

import json
import uuid
import faiss

from enum import Enum
from datetime import datetime, timedelta

from langchain.docstore import InMemoryDocstore
from langchain.memory import ChatMessageHistory
from langchain.vectorstores import FAISS, Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.retrievers import TimeWeightedVectorStoreRetriever
from langchain.schema import Document, AIMessage, HumanMessage, SystemMessage

class MemoryType(Enum):
    HISTORY = "history"
    SHORTTERM = "short_term"
    LONGTERM = "long_term"
    UNKNOWN = "unknown"
    
class Memory(object):
    def __init__(self) -> None:
        self.memory_type = MemoryType.UNKNOWN

    def add(self, key, value):
        raise NotImplementedError("Don't call the interface.")
    
    def delete(self, key):
        raise NotImplementedError("Don't call the interface.")
    
    def query(self, key, top_k):
        raise NotImplementedError("Don't call the interface.")
    
    def update(self, key, value):
        raise NotImplementedError("Don't call the interface.")
    
class History(Memory):
    def __init__(self):
        super().__init__()
        self.memory_type = MemoryType.HISTORY
        self.history_length = 0
        self.index = ChatMessageHistory()

    def add(self, key, value):
        if key == "user":
            self.index.add_user_message(value)
        elif key == "ai":
            self.index.add_ai_message(value)
        else:
            raise KeyError("Unknown History Key.")
    
    def query(self, top_k):
        return self.index.messages[-top_k:]

class ShortTermMemory(Memory):
    def __init__(self):
        super().__init__()
        self.memory_type = MemoryType.SHORTTERM
        self.embeddings_model = OpenAIEmbeddings()
        self.embedding_size = 1536
        self.decay_rate = 0.05
        self.top_k = 5
        self.vectorstore = FAISS(self.embeddings_model.embed_query, faiss.IndexFlatL2(self.embedding_size), InMemoryDocstore({}), {})
        self.retriever = TimeWeightedVectorStoreRetriever(vectorstore=self.vectorstore, decay_rate=self.decay_rate, k=self.top_k)
    
    def add(self, key, value):
        key_str = json.dumps(key)
        value_str = json.dumps(value)
        content = f"{key_str} -> {value_str}"
        self.retriever.add_documents([Document(page_content=content, metadata={"last_accessed_at": datetime.now()})])

    def query(self, key, top_k):
        return self.retriever.get_relevant_documents(key)[:top_k]
    
    def convert(self, docs):
        return [AIMessage(content=doc.page_content) for doc in docs]            


class LongTermMemory(Memory):
    def __init__(self) -> None:
        super().__init__()
        self.memory_type = MemoryType.LONGTERM
        self.embedding_function = OpenAIEmbeddings()
        self.index = Chroma(embedding_function=self.embedding_function, persist_directory='db')
        self.threshold = 0.75

        # Create an empty collection and persist it
        [self.index.add_texts([""]) for _ in range(5)]
        self.index.persist()

    def add(self, keys, values):
        key_embeddings = self.embedding_function.embed_documents(keys)

        key_ids = [str(uuid.uuid1()) for _ in keys]

        self.index._collection.add(
            embeddings=key_embeddings, documents=[values], ids=key_ids
        )
        self.index.persist()
    
    def query(self, key, top_k):
        docs = self.index.similarity_search_with_score(query=key, k=top_k)
        return [doc for doc in docs if doc[0] and doc[1] > self.threshold]
    
    def convert(self, docs):
        # return [SystemMessage(content=doc.page_content) for doc in docs]
        return None