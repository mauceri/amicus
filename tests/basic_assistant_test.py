import unittest
from os.path import dirname, abspath

from langchain_community.chat_models import ChatAnyscale, ChatOpenAI

from amicus.assistant.basic_assistant import *
from amicus.base.common_impl import *


class BasicAssistantTests (unittest.TestCase):

    BASE_DIR = dirname(dirname(abspath(__file__)))
    DATA_DIR = BASE_DIR + "/data_tests/"
    ENV_FILE = DATA_DIR + ".localenv"
    ANYSCALE_URL = "https://api.endpoints.anyscale.com/v1/chat/completions"
    ANYSCALE_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    ANYSCALE_TEMPERATURE = 0.7
    DB_FILE = DATA_DIR + "db.sqlite"
    LOG_FILE = DATA_DIR + "log.txt"

    def _createLLM (self) -> ChatOpenAI:
        AssistantService.loadEnvFile(BasicAssistantTests.ENV_FILE)
        AssistantService.setLoggingConfig( self.LOG_FILE )
        os.environ["ANYSCALE_API_BASE "] = self.ANYSCALE_URL
        llm = ChatAnyscale(model_name=self.ANYSCALE_MODEL)
        return llm

    def _createBasicAssistant(self ) -> Assistant:
        llm = self._createLLM()
        agent = BasicAssistant(llm, self.ANYSCALE_TEMPERATURE )
        return agent

    def _createAssistantService(self) -> AssistantService:
        assistant = self._createBasicAssistant()
        assistantService = DbAssistantService( assistant, self.DB_FILE )
        return assistantService

    def test_basic_assistant(self):
        assistant = self._createBasicAssistant()
        conversation="The yellow chamber"
        speaker = "Bob"
        messageIn = Message(conversation,
                           speaker,
                           assistant.getNow(),
                    "Quelle est la circonférence de la terre en une phrase?")
        assistantMessage, newConversation = assistant.processMessage(messageIn,
                                                                assistant.createConversation(conversation))
        self.assertIsNotNone(assistantMessage)
        self.assertIsNotNone(newConversation)

        logging.debug("Assistant reply = " + assistantMessage.content )
        print( "Assistant reply = " + assistantMessage.content)

    def test_assistant_service(self):
        assistantService = self._createAssistantService()

        conversationId="The yellow chamber"
        speaker = "Bob"
        messageIn = Message(conversationId,
                           speaker,
                           assistantService.getNow(),
                    "Quelle est la circonférence de la terre en une phrase?")

        assistantMessage = assistantService.processMessage(messageIn)
        self.assertIsNotNone(assistantMessage)

        logging.debug("Assistant reply = " + assistantMessage.content)
        print("Assistant reply = " + assistantMessage.content)


if __name__ == '__main__':
    unittest.main()
