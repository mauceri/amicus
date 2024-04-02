
from amicus.base.common_impl import *
from os.path import dirname, abspath
from dspy import *
from dsp.utils import deduplicate

prompt_1 = """
Génère un poème composé au plus de {lineNumber} vers ou lignes, chacunes comportant 12 pieds exactement.
Evite les répétitions de mots dans un même vers.
Ce poème évoque le sujet suivant: {subject}.
"""

class PoeticAssistant(Assistant):
    def __init__(self,
                 llm: Anyscale,
                 lineNumber:int):
        dspy.settings.configure(lm=llm)
        self.poemModel = SimplePoemModel(lineNumber)

    def processMessage(self,
                       inputMessage: Message,
                       conversation: Conversation) -> Tuple[Message, Conversation]:
        assistantAnswer = self.poemModel(inputMessage.content)
        assistantMessage = Message(conversation.id,
                                   "assistant",
                                   self.getNow(),
                                   assistantAnswer.poem)
        return assistantMessage, conversation

    def createConversation(self, conversationId: str) -> Conversation:
        return Conversation(conversationId)


class PoeticAssistantIPlugin(AbstractAssistantIPlugin):
    def __init__(self, observable: IObservable, dataDir: str = None, lineNumber: int = 4):
        self.BASE_DIR = dirname(dirname(abspath(__file__)))
        self.DATA_DIR = self.BASE_DIR + "/data/" if dataDir is None else dataDir
        self.ENV_FILE = self.DATA_DIR + ".localenv"
        self.ANYSCALE_URL = "https://api.endpoints.anyscale.com/v1"
        self.ANYSCALE_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"
        # self.ANYSCALE_MODEL = "meta-llama/Llama-2-70b-chat-hf"
        self.ANYSCALE_TEMPERATURE = 0.2
        self.ANYSCALE_MAX_TOKENS = 1000
        self.DB_FILE = self.DATA_DIR + "db.sqlite"
        self.LOG_FILE = self.DATA_DIR + "log.txt"
        assistantService = self._createAssistantService(lineNumber)
        AbstractAssistantIPlugin.__init__(self, assistantService, observable)

    def _createLLM (self) -> Anyscale:
        AssistantService.loadEnvFile(self.ENV_FILE)
        AssistantService.setLoggingConfig( self.LOG_FILE )
        os.environ["ANYSCALE_API_BASE"] = self.ANYSCALE_URL
        llm = Anyscale(model=self.ANYSCALE_MODEL,
                       temperature=self.ANYSCALE_TEMPERATURE,
                       use_chat_api=True,
                       max_tokens=self.ANYSCALE_MAX_TOKENS)
        return llm

    def _createAssistant(self, lineNumber: int) -> Assistant:
        llm = self._createLLM()
        agent = PoeticAssistant(llm, lineNumber )
        return agent

    def _createAssistantService(self,lineNumber: int) -> AssistantService:
        assistant = self._createAssistant(lineNumber)
        assistantService = DbAssistantService( assistant, self.DB_FILE )
        return assistantService


class PoemGenerator(dspy.Signature):
    """Génère un poème répondant à un sujet"""

    subject = dspy.InputField(desc="Décrit le sujet du poème")
    lineNumber = dspy.InputField(desc="Le nombre de ligne ou de vers qui composent le poème")
    poem = dspy.OutputField(desc="Le poème en alexandrin correspondant sujet")


class SimplePoemModel(dspy.Module):
    """
    Provide answer to question
    """
    def __init__(self, lineNumber: int):
        super().__init__()
        self.lineNumber = lineNumber
        self.poemGenerator = dspy.Predict(PoemGenerator)

    def forward(self, subject):
        prePromptSubject = prompt_1.format( lineNumber=self.lineNumber, subject=subject)
        poem = self.poemGenerator(
            subject = prePromptSubject,
            lineNumber = str(self.lineNumber))
        return poem