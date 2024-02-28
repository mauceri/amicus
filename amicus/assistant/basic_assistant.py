from langchain_community.chat_models import ChatAnyscale, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from amicus.base.common import *
from amicus.base.common_impl import *
from datetime import datetime
from langchain_core.pydantic_v1 import BaseModel, Field
from os.path import dirname, abspath


class BasicAssistant(Assistant):
    def __init__(self,
                 llm: ChatOpenAI,
                 llmTemperature: str):
        self._llm = llm
        self._llmTemperature = llmTemperature
        promptStr = "Vous êtes un robot de discussion générale. Vos réponses sont concises, elles ne dépassent pas 100 mots, mais restent informatives. {input} "
        prompt = ChatPromptTemplate.from_template(promptStr)
        self._chain = prompt | self._llm

    def processMessage(self,
                       inputMessage: Message,
                       conversation: Conversation) -> Tuple[Message, Conversation]:
        assistantReply = self._chain.invoke( {"input": inputMessage.content  } )
        assistantMessage = Message(conversation.id, "assistant", self.getNow(), assistantReply.content)
        return assistantMessage, conversation

    def createConversation(self, conversationId: str) -> Conversation:
        return Conversation(conversationId)


class BasicAssistantIPlugin(AbstractAssistantIPlugin):
    def __init__(self, observable: IObservable, dataDir: str = None):
        self.BASE_DIR = dirname(dirname(abspath(__file__)))
        self.DATA_DIR = self.BASE_DIR + "/data/" if dataDir is None else dataDir
        self.ENV_FILE = self.DATA_DIR + ".localenv"
        self.ANYSCALE_URL = "https://api.endpoints.anyscale.com/v1/chat/completions"
        self.ANYSCALE_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"
        self.DB_FILE = self.DATA_DIR + "db.sqlite"
        self.LOG_FILE = self.DATA_DIR + "log.txt"

        AbstractAssistantIPlugin.__init__(BasicAssistant, observable)

    def _createLLM(self) -> BaseModel:
        Assistant.readEnvFile(self.ENV_FILE)
        os.environ["ANYSCALE_API_BASE "] = self.ANYSCALE_URL
        llm = ChatAnyscale(model_name=self.ANYSCALE_MODEL)
        return llm

    def _createBasicAssistant(self) -> Assistant:
        llm = self._createLLM()
        agent = BasicAssistant(llm, self.ANYSCALE_TEMPERATURE)
        return agent

    def _createAssistantService(self) -> AssistantService:
        assistant = self._createBasicAssistant()
        assistantService = DbAssistantService(assistant, self.DB_FILE)
        return assistantService
