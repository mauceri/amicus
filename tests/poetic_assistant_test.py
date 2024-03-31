import unittest
from os.path import dirname, abspath

from langchain_community.chat_models import ChatAnyscale, ChatOpenAI

from amicus.assistant.poetic_assistant import PoeticAssistant, PoeticAssistantIPlugin
from amicus.base.common_impl import *
import time
from dspy import *

class PoeticAssistantTests (unittest.TestCase):

    BASE_DIR = dirname(dirname(abspath(__file__)))
    DATA_DIR = BASE_DIR + "/data_tests/"
    ENV_FILE = DATA_DIR + ".localenv"
    ANYSCALE_URL = "https://api.endpoints.anyscale.com/v1"
    ANYSCALE_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    #ANYSCALE_MODEL = "meta-llama/Llama-2-70b-chat-hf"
    ANYSCALE_MAX_TOKENS = 1000
    ANYSCALE_TEMPERATURE = 0.2
    DB_FILE = DATA_DIR + "db.sqlite"
    LOG_FILE = DATA_DIR + "log.txt"


    def _createLLM (self) -> Anyscale:
        AssistantService.loadEnvFile(self.ENV_FILE)
        AssistantService.setLoggingConfig( self.LOG_FILE )
        os.environ["ANYSCALE_API_BASE"] = self.ANYSCALE_URL
        llm = Anyscale(model=self.ANYSCALE_MODEL,
                       temperature=self.ANYSCALE_TEMPERATURE,
                       use_chat_api=True,
                       max_tokens=self.ANYSCALE_MAX_TOKENS)
        return llm

    def _createAssistant(self, lineNumber:int) -> Assistant:
        llm = self._createLLM()
        agent = PoeticAssistant(llm,lineNumber)
        return agent

    def _createAssistantService(self) -> AssistantService:
        assistant = self._createAssistant()
        assistantService = DbAssistantService( assistant, self.DB_FILE )
        return assistantService

    def test_poetic_assistant_zeroshot(self):
        lineNumber = 4
        assistant = self._createAssistant(lineNumber)
        conversation="The poetic chamber"
        speaker = "Victor"
        messageIn = Message(conversation,
                           speaker,
                           assistant.getNow(),
                    "l'importance de l'ordinateur dans nos vies modernes, poème en français.")
        assistantMessage, newConversation = assistant.processMessage(messageIn,
                                                                assistant.createConversation(conversation))
        self.assertIsNotNone(assistantMessage)
        self.assertIsNotNone(newConversation)

        logging.debug("Assistant reply = " + assistantMessage.content )
        print( "Assistant reply = " + assistantMessage.content)


    def test_assistant_service_zeroshot(self):
        multihop = False
        assistantService = self._createAssistantService(multihop)

        conversationId="The yellow chamber"
        speaker = "Bob"
        messageIn = Message(conversationId,
                           speaker,
                           assistantService.getNow(),
                    "What is the circonference of the planet Mars?")

        assistantMessage = assistantService.processMessage(messageIn)
        self.assertIsNotNone(assistantMessage)

        logging.debug("Assistant reply = " + assistantMessage.content)
        print("Assistant reply = " + assistantMessage.content)

    def test_assistant_service_multihop(self):
        multihop = True
        assistantService = self._createAssistantService(multihop)

        conversationId="The yellow chamber"
        speaker = "Bob"
        messageIn = Message(conversationId,
                           speaker,
                           assistantService.getNow(),
                    "What is the circonference of the planet Mars?")

        assistantMessage = assistantService.processMessage(messageIn)
        self.assertIsNotNone(assistantMessage)

        logging.debug("Assistant reply = " + assistantMessage.content)
        print("Assistant reply = " + assistantMessage.content)

    def test_assistant_pluggin_sync (self):
        # not operational
        inputObservable = TestIObservable()
        assistantPluggin = DSPyAssistantIPlugin ( inputObservable, self.DATA_DIR )
        assistantPluggin.start()
        roomId = "myRoom"
        event = {"event_id": "id1", "sender": "Smith and Wesson", "origin_server_ts": 1234}
        message = "what is the radius of the earth?"
        event = RoomMessageText(event, message, message, None)
        room = MatrixRoom( "room id 1", "user id 1")
        inputObservable.onRoomEvent_sync(room,event,message)
        self.assertEqual( "Smith and Wesson", event.sender )
        self.assertEqual( event, inputObservable.lastNotifiedEvent )
        self.assertTrue(  inputObservable.lastNotifiedMessage.find("6,371")>=0 )
        assistantPluggin.stop()

    def test_assistant_pluggin_async (self):
        # not operational
        inputObservable = TestIObservable()
        assistantPluggin = BasicAssistantIPlugin ( inputObservable, self.DATA_DIR )
        assistantPluggin.start()
        roomId = "myRoom"
        event = {"event_id": "id1", "sender": "Smith and Wesson", "origin_server_ts": 1234}
        message = "what is the radius of the earth?"
        event = RoomMessageText(event, message, message, None)
        room = MatrixRoom( "room id 1", "user id 1")
        inputObservable.onRoomEvent(room,event,message)
        time.sleep(10)
        self.assertEqual( "Smith and Wesson", event.sender )
        self.assertEqual( event, inputObservable.lastNotifiedEvent )
        self.assertTrue(  inputObservable.lastNotifiedMessage.find("6,371") )
        assistantPluggin.stop()


class TestIObservable(IObservable):

    def subscribe(self, observer: IObserver):
        self._observer = observer

    def unsubscribe(self, observer: IObserver):
        self._observer = None

    def onRoomEvent_sync (self, room: MatrixRoom, event: RoomMessageText, message: str, filepath: str = None,
               filename: str = None):
        self._observer.notify_sync(room, event, message)
        print("TestIOObservable", message)

    async def onRoomEvent(self, room: MatrixRoom, event: RoomMessageText, message: str, filepath: str = None,
                         filename: str = None):
        await self._observer.notify(room, event, message)
        print("TestIOObservable", message)

    def notify(self, room: MatrixRoom, event: RoomMessageText, message: str, filepath: str = None,
               filename: str = None):
        self.lastNotifiedEvent = event
        self.lastNotifiedMessage = message
        print("TestIOObservable", message)


if __name__ == '__main__':
    unittest.main()
