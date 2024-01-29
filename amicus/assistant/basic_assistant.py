from amicus.base.common import *
from datetime import datetime


class BasicAssistant (Assistant):
    def __init__(self, llm: LLM, dataConfiguration: DataConfiguration):
        self.llm = llm
        self.dataConfiguration = dataConfiguration

    def processSpeech(self,
                       inputSpeech: Speech,
                       conversation: Conversation) -> Tuple[Speech, Conversation]:
        prompt = "Vous êtes un robot de discussion générale. Vos réponses sont concises, elles ne dépassent pas 500 mots, mais restent informatives."
        llmOutput = self.llm.sendMessage(prompt,
                             inputSpeech.content,
                             self.dataConfiguration.llmTemperature )
        return Speech(conversation.id, "assistant", self._getNow(), llmOutput), conversation

    def createConversation(self, conversationId: str) -> Conversation:
        return Conversation(conversationId)

    def _getNow(self) -> str:
        return datetime.now().isoformat()

