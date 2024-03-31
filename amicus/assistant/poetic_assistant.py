
from amicus.base.common_impl import *
from os.path import dirname, abspath
from dspy import *
from dsp.utils import deduplicate


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
    def __init__(self, observable: IObservable, dataDir: str = None, multihop = True):
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
        assistantService = self._createAssistantService(multihop)
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

    def _createAssistant(self,  multihop: bool ) -> Assistant:
        llm = self._createLLM()
        agent = PoeticAssistant(llm )
        return agent

    def _createAssistantService(self,  multihop: bool) -> AssistantService:
        assistant = self._createAssistant(multihop)
        assistantService = DbAssistantService( assistant, self.DB_FILE )
        return assistantService


class PoemGenerator(dspy.Signature):
    """Génère un poème répondant à un sujet"""

    subject = dspy.InputField(desc="Décrit le sujet du poème")
    lineNumber = dspy.InputField(desc="Le nombre de ligne ou de vers composant le poème")
    poem = dspy.OutputField(desc="Le poeme en alexandrins répondant aux demandes du sujet")


class SimplePoemModel(dspy.Module):
    """
    Provide answer to question
    """
    def __init__(self, lineNumber: int):
        super().__init__()
        self.lineNumber = lineNumber
        self.poemGenerator = dspy.Predict(PoemGenerator)

    def forward(self, subject):
        poem = self.poemGenerator(
            subject = "Génère un poème composé au plus de 4 vers dont chacun comporte 12 pieds exactement. Ce poème évoque le sujet suivant:" + subject,
            lineNumber = str(self.lineNumber))
        return poem