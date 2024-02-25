import unittest
from os.path import dirname, abspath

from langchain_community.chat_models import ChatAnyscale

from amicus.assistant.langchain_assistant import *
from amicus.assistant.themis_assistant import *

from amicus.base.common_impl import *


class ThemisAssistantTests (unittest.TestCase):

    REPERTOIRE_BASE = dirname(dirname(abspath(__file__)))
    REPERTOIRE_DATA = REPERTOIRE_BASE + "/data_tests"

    ANYSCALE_API_KEY = "esecret_e8yd4kit37yxtqf4zrhbcylji4"
    ANYSCALE_API_BASE = "https://api.endpoints.anyscale.com/v1/chat/completions"
    ANYSCALE_MODEL_NAME = "mistralai/Mixtral-8x7B-Instruct-v0.1"

    def test_decision_service(self):
        decisionService = DecisionService()
        riskResume = decisionService.summeriseRiskLevel()
        self.assertIsNotNone(riskResume)
        print( "At 0, risk level =", riskResume)

        decisionService.changeThreatLevel( 0.5 )
        riskResume = decisionService.summeriseRiskLevel()
        print( "At 1, Risk level =", riskResume)
        recommend =  decisionService.recommendMitigationLevel( .3 )
        self.assertIsNotNone(recommend)
        print( "Recommendation: ", recommend)

        decisionService.changeMitigationLevel(1.0)
        riskResume = decisionService.summeriseRiskLevel()
        print( "At 2, Risk level =", riskResume)


    def test_assistant_1(self):

        os.environ["ANYSCALE_API_KEY"] = self.ANYSCALE_API_KEY
        os.environ["ANYSCALE_API_BASE "] = self.ANYSCALE_API_BASE

        llm = ChatAnyscale(model_name=self.ANYSCALE_MODEL_NAME)
        verbose = True
        assistant = ThemisAssistant(llm, verbose)

        conversation = assistant.createConversation(0)
        speech = Speech(conversation.id, "John Smith", assistant.getNow(),
                        "Could you give me the level of risk please?" )
        print("Question", speech.content)
        respons = assistant.processSpeech(speech, conversation)
        print("Respons", respons.content)


    def test_assistant_2(self):
        os.environ["ANYSCALE_API_KEY"] = self.ANYSCALE_API_KEY
        os.environ["ANYSCALE_API_BASE "] = self.ANYSCALE_API_BASE

        llm = ChatAnyscale(model_name=self.ANYSCALE_MODEL_NAME)
        verbose = True
        assistant = ThemisAssistant(llm, verbose)

        conversation = assistant.createConversation(0)
        speech = Speech(conversation.id, "John Smith", assistant.getNow(),
                        "Increase the level of the threat to 0.5?")
        print("Question", speech.content)
        respons = assistant.processSpeech(speech, conversation)

        speech = Speech(conversation.id, "John Smith", assistant.getNow(),
                        "Give me now the risk level?")
        print("Question", speech.content)
        respons = assistant.processSpeech(speech, conversation)
        print("Respons", respons.content)


    def test_assistant_3(self):
        os.environ["ANYSCALE_API_KEY"] = self.ANYSCALE_API_KEY
        os.environ["ANYSCALE_API_BASE "] = self.ANYSCALE_API_BASE

        llm = ChatAnyscale(model_name=self.ANYSCALE_MODEL_NAME)
        verbose = True
        assistant = ThemisAssistant(llm, verbose)

        conversation = assistant.createConversation(0)
        speech = Speech(conversation.id, "John Smith", assistant.getNow(),
                        "Increase the level of the threat to 0.5?")
        print("Question", speech.content)
        respons = assistant.processSpeech(speech, conversation)
        print("Respons", respons.content)

        speech = Speech(conversation.id, "John Smith", assistant.getNow(),
                        "Recommend a mitigation level for a maximum risk of 0.3")
        print("Question", speech.content)
        respons = assistant.processSpeech(speech, conversation)
        print("Respons", respons.content)



if __name__ == '__main__':
    unittest.main()
