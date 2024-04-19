from langchain_community.chat_models import ChatAnyscale, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from amicus.assistant.basic_assistant import BasicAssistantIPlugin
from amicus.assistant.dspy_assistant import DSPyAssistantIPlugin
from amicus.assistant.poetic_assistant import PoeticAssistantIPlugin
from amicus.base.common import *
from amicus.base.common_impl import *
from datetime import datetime
from langchain_core.pydantic_v1 import BaseModel, Field
from os.path import dirname, abspath


class Plugin(IPlugin):
    def __init__(self,observable:IObservable):
        self.__observable = observable
#        self.ba = BasicAssistantIPlugin(observable,"/data/amicus_adiutor/ba","!ba")
#        logger.info(f"********************** Observateur créé {self.ba.prefix()}")
#        self.dspya = DSPyAssistantIPlugin(observable,"/data/amicus_adiutor/dspya","!dspya")
#        logger.info(f"********************** Observateur créé {self.dspya.prefix()}")
        self.poema = PoeticAssistantIPlugin(observable,"/data/amicus_adiutor/poema","!poema")
        logger.info(f"********************** Observateur créé {self.poema.prefix()}")
        
        
    def start(self):
        logger.info(f"********************** Inscription de {self.ba.prefix()}")
        self.ba.start()
        logger.info(f"********************** Inscription de {self.dspya.prefix()}")
        self.dspya.start()
        logger.info(f"********************** Inscription de {self.poema.prefix()}")
        self.poema.start()

    async def stop(self):
        self.ba.stop() 
        self.dspya.stop()
        self.poema.stop()

