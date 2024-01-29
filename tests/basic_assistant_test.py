import unittest
from os.path import dirname, abspath

from amicus.assistant.basic_assistant import *
from amicus.base.common_impl import *


class AssistantTests (unittest.TestCase):

    REPERTOIRE_BASE = dirname(dirname(abspath(__file__)))
    REPERTOIRE_DATA = REPERTOIRE_BASE + "/data_tests"

    def _createDataConfiguration(self):
        dataConf = DataConfiguration (self.REPERTOIRE_DATA,
                                            ".localenv",
                                            "test_db.sqlite",
                                            "https://api.endpoints.anyscale.com/v1/chat/completions",
                                            "mistralai/Mixtral-8x7B-Instruct-v0.1",
                                            "ANY_SCALE_API_KEY",
                                            0.7)

        dataConf.setLoggingConfig("test_log.txt")
        logging.debug("test data conf")
        return dataConf

    def _getNow(self) -> str:
        return datetime.now().isoformat()

    def test_basic_assistant(self):
        dataConf = self._createDataConfiguration()
        llm = AnyScaleLLM(dataConf)
        agent = BasicAssistant(llm, dataConf)
        conversation="The yellow chamber"
        speaker = "Bob"
        speechIn = Speech(conversation,
                           speaker,
                            self._getNow(),
                    "Quelle est la circonférence de la terre en une phrase?")
        assistantSpeech, newConversation = agent.processSpeech(speechIn,
                                                        agent.createConversation(conversation))
        self.assertIsNotNone(assistantSpeech)
        self.assertIsNotNone(newConversation)

        logging.debug("Assistant reply = " + assistantSpeech.content )
        print( "Assistant reply = " + assistantSpeech.content)


    def test_conversation_pool(self):
        dataConf = self._createDataConfiguration()
        llm = AnyScaleLLM(dataConf)
        assistant = BasicAssistant(llm, dataConf)

        conversation="The yellow chamber"
        speaker = "Bob"
        speechIn = Speech(conversation,
                           speaker,
                            self._getNow(),
                    "Quelle est la circonférence de la terre en une phrase?")

        conversationService = ConversationServiceImpl(dataConf, assistant)
        assistantSpeech = conversationService.processSpeech(speechIn)
        self.assertIsNotNone(assistantSpeech)

        logging.debug("Assistant reply = " + assistantSpeech.content)
        print("Assistant reply = " + assistantSpeech.content)

    def test_data_config_persistence(self):
        dataConfig = self._createDataConfiguration()
        jsonFileFqn = dataConfig.dataDir + "/dataConfigTest.json"
        dataConfig.saveAsJson(jsonFileFqn)
        dataConfigRead: DataConfiguration = DataConfiguration.loadFromJson(jsonFileFqn)
        self.assertIsNotNone(dataConfigRead)
        self.assertEqual(dataConfigRead.dataDir, self.REPERTOIRE_DATA )

if __name__ == '__main__':
    unittest.main()
