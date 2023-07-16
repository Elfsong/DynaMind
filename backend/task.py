# coding: utf-8
# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2023-04-29

import json
import utils
import prompt
import requests
from tqdm import tqdm
from enum import Enum
from termcolor import cprint
from langchain.chat_models import ChatOpenAI
from langchain.utilities import BingSearchAPIWrapper
from langchain.document_loaders import PlaywrightURLLoader
from langchain.schema import Document, AIMessage, HumanMessage, SystemMessage


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
        self.smart_llm_token_limit = 8000
        self.fast_llm_token_limit = 4000
    
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
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, request_timeout=300)

    def execute(self):
        math_messages = prompt.math_prompt.format_messages(question=self.question)

        # Inference
        result = self.llm(math_messages)
        return result.content

class SearchTask(Task):
    def __init__(self, name, args) -> None:
        super().__init__(name, args)
        self.task_type = TaskType.SEARCH
        self.query = self.args["query"]
        self.top_k = 5 # TODO(mignzhe): config
        self.search_engine = BingSearchAPIWrapper()
    
    def cisco_search(self):
        try:
            url = "https://search.cisco.com/services/search"

            payload = json.dumps({
                "query": self.query,
                "startIndex": 0,
                "count": "50",
                "searchType": "CISCO",
                "tabName": "Cisco",
                "debugScoreExplain": False,
                "facets": [],
                "sortType": "RELEVANCY",
                "dynamicRelevancyId": "",
                "categoryValue": "Cisco 500 Series WPAN Industrial Routers",
                "breakpoint": "L",
                "searchProfile": "",
                "ui": "one",
                "searchCat": "",
                "searchMode": "text",
                "callId": "MqgFtek84g",
                "requestId": 1676997244167,
                "taReqId": "1676996834071",
                "bizCtxt": "",
                "qnaTopic": [],
                "appName": "CDCSearchFE",
                "social": False,
                "localeStr": "enUS",
                "onlyOrganic": False,
                "ppscountry": "",
                "ppslanguage": "",
                "ppsjobrole": False,
                "pq": "",
                "pq_cat": "",
                "additionalParams": ""
            })
            headers = {
                'authority': 'search.cisco.com',
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,zh;q=0.6',
                'content-type': 'application/json',
                'cookie': '_cs_c=0; UnicaNIODID=undefined; _gcl_au=1.1.148050418.1675083872; aam_uuid=81665194308821499492291952182538275165; _biz_uid=13b12fdc333d412fe5efb12a7b953edd; ORA_FPC=id=7d62ae1f-0d88-4df7-a70e-c842d822ac77; OptanonAlertBoxClosed=2023-01-30T13:05:06.219Z; _gscu_1403625542=75084248z3d7uo54; _mkto_trk=id:564-WHV-323&token:_mch-cisco.com-1675084440194-64906; Hm_lvt_a804d9548837e94caa5dc76086a8154f=1675084247,1675513224; ELOQUA=GUID=9B35670EC25E429A8513EF4E647ED7D2&FPCVISITED=1; _biz_flagsA=%7B%22Version%22%3A1%2C%22Ecid%22%3A%221075060619%22%2C%22ViewThrough%22%3A%221%22%2C%22XDomain%22%3A%221%22%2C%22Frm%22%3A%221%22%7D; _ga_MB8Q5XRDJJ=GS1.1.1675514056.2.1.1675514116.0.0.0; AMCVS_B8D07FF4520E94C10A490D4C%40AdobeOrg=1; cdcUniqueKey=ce074507j31h7; check=true; _gid=GA1.2.1753824503.1676861527; anchorvalue=; _ga=GA1.2.1105767920.1675083873; _ga_KP8QEFW4ML=GS1.1.1676878464.6.1.1676880756.60.0.0; aam_uuid=81665194308821499492291952182538275165; _abck=ADC73596B4FFE05BE6EA60E4B6C9754B~0~YAAQLMvcF6elUWuGAQAA3vk1cQmtdkfTgkRxtZZ/AUHk7qKqDn7Bj2C+ThbiiJPcyhZcCzvTf0lMZDTOymozJq2Pm+nyJi47rn04SptLGoiomCVsdGDLT04AcXXkWNy+DSHGtu8ran8i6F92y8TLfgQeSWQ5tqecVTyVcsad+xqjP9STNUHGSSO4nBpcFKjcsFJLQxdjygOUYFWZuPsY6re++Khd0tKRitcxZ/0C7BFAWuDbKvGIVFntlWZsu5OwtFy6bn0v8w4UeaOyTXosgQPJHLaR23G9YWLBOEa8/kJf11RBFdZi0qPYN6RC3tKnHEqXNg/Vi0jLTqboSbZtZjR5HIdnLIzOkMtC9NGSYe0D98tt+ZreJ8ZrqiXorDfuM2YpU+maTbJfgSD48RiTvew0bB2lP0c=~-1~||-1||~-1; _cs_cvars=%7B%222%22%3A%5B%22Template%20Name%22%2C%22supporthomepage_20%22%5D%2C%223%22%3A%5B%22Title%22%2C%22support%20-%20cisco%20support%20and%20downloads%20%E2%80%93%20documentation%2C%20tools%2C%20cases%22%5D%2C%224%22%3A%5B%22Page%20Channel%22%2C%22technical%20support%22%5D%2C%225%22%3A%5B%22Page%20Name%22%2C%22cisco.com%2Fc%2Fen%2Fus%2Fsupport%2Findex.html%22%5D%2C%226%22%3A%5B%22Content%20Type%22%2C%22postsales%22%5D%7D; CP_GUTC=23.50.232.106.272801676952870990; ADRUM=s=1676979479889&r=https%3A%2F%2Fwww.cisco.com%2Fc%2Fen%2Fus%2Fsupport%2Fsecurity%2Findex.html; _uetsid=90094b60b0c911ed821e79548e95a7d9; _uetvid=a5ce3df059b311edbc8ad9e12a380133; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Feb+21+2023+23%3A39%3A58+GMT%2B0800+(Singapore+Standard+Time)&version=6.39.0&isIABGlobal=false&hosts=&consentId=8ee11340-fdbe-4a2f-bd3e-d896a41df0c1&interactionCount=1&landingPath=NotLandingPage&groups=1%3A1%2C2%3A1%2C3%3A1%2C4%3A1&AwaitingReconsent=false&geolocation=SG%3B; _biz_nA=238; s_cc=true; WTPERSIST=cisco.gutcid=23.50.232.106.272801676952870990&ora.eloqua=9b35670ec25e429a8513ef4e647ed7d2&cisco.mid=87068195414001827161607572055450456284&cisco.aam_uuid=81665194308821499492291952182538275165&cisco._ga=GA1.2.1105767920.1675083873&cisco.account_or_company_id=sav_203808807; _biz_pendingA=%5B%5D; _cs_id=f58923c4-2645-a49e-d3a8-10741cef96ed.1667531444.17.1676971098.1676971098.1589297132.1701695444411; gpv_v9=search.cisco.com%2Fsearch; mbox=session#bfc535eace8b46b387e986a52c3bf62b#1676998695; AMCV_B8D07FF4520E94C10A490D4C%40AdobeOrg=281789898%7CMCIDTS%7C19409%7CMCMID%7C87068195414001827161607572055450456284%7CMCAAMLH-1677601640%7C3%7CMCAAMB-1677601640%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1677004040s%7CNONE%7CMCAID%7CNONE%7CMCCIDH%7C479621989%7CvVersion%7C4.1.0; utag_main=v_id:018602c76a780080cca57be0f2a005075006006d00e50$_sn:9$_ss:0$_st:1676998650559$vapi_domain:cisco.com$_se:143$unique_visitor:true$ses_id:1676996138834%3Bexp-session$_pn:1%3Bexp-session$ctm_ss:true%3Bexp-session; s_sq=%5B%5BB%5D%5D; JSESSIONID=06D2B5574DFD5902CADF798416FB7872; s_ptc=0%5E%5E0%5E%5E0%5E%5E0%5E%5E76%5E%5E1%5E%5E1061%5E%5E15%5E%5E1164; s_ppvl=cisco.com%2Fc%2Fen%2Fus%2Fsupport%2Fall-products.html%2C95%2C95%2C1408%2C2560%2C1329%2C2560%2C1440%2C1%2CP; s_ppv=search.cisco.com%2Fsearch%2C9%2C9%2C1329%2C1479%2C1329%2C2560%2C1440%2C1%2CP; ADRUM_BT1="R:249|i:574697|e:3312"; ADRUM_BTa="R:249|g:d483c5fb-8edc-4e1e-9b96-9b5e84252e4a|n:cisco1_d5ce4a50-0e7c-4e42-a5a5-4c7d1bcfcd74"; JSESSIONID=784AFA84ECCD56BCC22183DC56B92A13; SameSite=None',
                'origin': 'https://search.cisco.com',
                'referer': 'https://search.cisco.com/search?locale=enUS&query=500%20Series%20WPAN%20Industrial%20Routers%20Configuration&bizcontext=&mode=text&clktyp=button&autosuggest=false&categoryvalue=Cisco%20500%20Series%20WPAN%20Industrial%20Routers&tareqid=1676996834071',
                'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            response_json = response.json()

            candidates = list()
            for item in response_json["items"][:2]:
                candidates += [{
                    "title": item["title"],
                    "content": item["content"],
                    "url": item["url"]
                }]
        except Exception as e:
            candidates = []

        return candidates

    def execute(self):
        bing_candidates = self.search_engine.results(self.query, self.top_k)
        # cisco_candidates = self.cisco_search()
        candidates = bing_candidates
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

    def execute(self):
        if self.file_type == "html":
            loader = PlaywrightURLLoader(urls=[self.file_path], remove_selectors=["header", "footer"])
        raw_data = loader.load()

        if raw_data:
            result = utils.recursive_summary(self.llm, raw_data[0].page_content, self.question, text_length=800, chunk_size=1000)
        else:
            result = ""

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

        # Inference
        result = self.llm(summary_messages)
        return result.content
        
class PLANTask(Task):
    def __init__(self, name, args) -> None:
        super().__init__(name, args)
        self.task_type = TaskType.PLAN

        # Model Selection
        self.llm = self.fast_llm if self.args["fast_model"] else self.smart_llm
        self.token_quota = self.fast_llm_token_limit if self.args["fast_model"] else self.smart_llm_token_limit
    
    def execute(self):
        # Prefix Prompt Construction
        prefix_messages = self.args["prefix_messages"]
        self.token_quota -= self.llm.get_num_tokens_from_messages(prefix_messages)

        # History retrieval
        history_list = self.args["history"]
        history_messages = list()
        history_quota = min(1000, self.token_quota - 4000)
        while history_list:
            history_messages += [history_list.pop()]
            history_messages_count = self.llm.get_num_tokens_from_messages(history_messages)
            if history_quota - history_messages_count < 0:
                history_messages.pop()
                print("History section too long, truncated...")
                break
        history_messages.reverse()
        self.token_quota -= self.llm.get_num_tokens_from_messages(history_messages)

        # # Action History Retrieval
        # action_history_list = self.args["action_history"]
        # action_history_messages = list()
        # action_history_quota = min(500, self.token_quota - 3500)
        # while action_history_list:
        #     action_history_messages += [action_history_list.pop()]
        #     action_history_messages_count = self.llm.get_num_tokens_from_messages(action_history_messages)
        #     if action_history_quota - action_history_messages_count < 0:
        #         action_history_messages.pop()
        #         break

        # Short-term memory retrieval
        short_term_list = self.args["short_term_memory"]
        short_term_messages = list()
        short_term_uuids = list()
        short_term_quota = min(5000, self.token_quota - 2000)
        while short_term_list:
            doc_message, doc_metadata = short_term_list.pop()

            # Summarize resource
            doc_message.content = utils.recursive_summary(llm=self.fast_llm, raw_text=doc_message.content, question=self.args["query"], text_length=1200, chunk_size=800)

            short_term_messages += [doc_message]
            short_term_uuids += [doc_metadata["uuid"]]
            short_term_messages_count = self.llm.get_num_tokens_from_messages(short_term_messages)
            if short_term_quota - short_term_messages_count < 0:
                poped_message = short_term_messages.pop()
                cprint(poped_message, 'red')
                short_term_uuids.pop()
                break
        self.token_quota -= self.llm.get_num_tokens_from_messages(short_term_messages)

        # Long-term memory retrieval
        long_term_list = self.args["long_term_memory"]
        long_term_messages = list()
        long_term_quota = min(3000, self.token_quota - 1000)
        while long_term_list:
            doc_message = long_term_list.pop()

            # Summarize resource
            doc_message.content = utils.recursive_summary(llm=self.fast_llm, raw_text=doc_message.content, question=self.args["query"], text_length=500, chunk_size=1000)

            long_term_messages += [doc_message]
            long_term_messages_count = self.llm.get_num_tokens_from_messages(long_term_messages)
            if long_term_quota - long_term_messages_count < 0:
                long_term_messages.pop()
                break
        self.token_quota -= self.llm.get_num_tokens_from_messages(long_term_messages)

        # Final guidance
        guidance_message = SystemMessage(content="Using the context knowledge to response.")

        # Inference
        cprint(f"short_term_messages: {short_term_messages}", color="red")
        cprint(f"long_term_messages: {long_term_messages}", color="blue")

        result = self.llm(prefix_messages + short_term_messages + long_term_messages + history_messages + [guidance_message])
        cprint(result, color="green")
        return utils.response_parse(result.content), short_term_uuids