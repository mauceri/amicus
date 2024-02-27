from amicus.base.common import *
from amicus.base.common_impl import *
from datetime import datetime
from langchain_core.pydantic_v1 import BaseModel, Field
from os.path import dirname, abspath


class BasicAssistant (Assistant):
    def __init__(self,
                 llm: BaseModel, dataConfiguration: DataConfiguration):
        self.llm = llm
        self.dataConfiguration = dataConfiguration

    def processMessage(self,
                       inputSpeech: Message,
                       conversation: Conversation) -> Tuple[Message, Conversation]:
        prompt = "Vous êtes un robot de discussion générale. Vos réponses sont concises, elles ne dépassent pas 500 mots, mais restent informatives."
        llmOutput = self.llm.sendMessage(prompt,
                             inputSpeech.content,
                             self.dataConfiguration.llmTemperature )
        return Message(conversation.id, "assistant", self.getNow(), llmOutput), conversation

    def createConversation(self, conversationId: str) -> Conversation:
        return Conversation(conversationId)


class BasicAssistantIPlugin (AbstractAssistantIPlugin):
    def __init__(self):
        REPERTOIRE_BASE = dirname(dirname(abspath(__file__)))
        REPERTOIRE_DATA = REPERTOIRE_BASE + "/data"
        dataConf = DataConfiguration(self.REPERTOIRE_DATA,
                                     ".localenv",
                                     "basic_assistant_db.sqlite",
                                     "https://api.endpoints.anyscale.com/v1/chat/completions",
                                     "mistralai/Mixtral-8x7B-Instruct-v0.1",
                                     "ANY_SCALE_API_KEY",
                                     0.7)
        dataConfiguration = DataConfiguration()
        AbstractAssistantIPlugin.__init__( BasicAssistant)

