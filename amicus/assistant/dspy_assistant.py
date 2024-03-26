
from amicus.base.common_impl import *
from os.path import dirname, abspath
from dspy import *
from dsp.utils import deduplicate


class DSPyAssistant(Assistant):
    def __init__(self,
                 llm: Anyscale,
                 retrievalManager: object):
        dspy.settings.configure(lm=llm, rm=retrievalManager)
        #self.answererModel = MultiHopModel()
        self.answererModel = ZeroShotModel()

    def processMessage(self,
                       inputMessage: Message,
                       conversation: Conversation) -> Tuple[Message, Conversation]:
        assistantAnswer = self.answererModel(inputMessage.content)
        assistantMessage = Message(conversation.id,
                                   "assistant",
                                   self.getNow(),
                                   assistantAnswer.answer)
        return assistantMessage, conversation

    def createConversation(self, conversationId: str) -> Conversation:
        return Conversation(conversationId)


class DSPyAssistantIPlugin(AbstractAssistantIPlugin):
    def __init__(self, observable: IObservable, dataDir: str = None):
        self.BASE_DIR = dirname(dirname(abspath(__file__)))
        self.DATA_DIR = self.BASE_DIR + "/data/" if dataDir is None else dataDir
        self.ENV_FILE = self.DATA_DIR + ".localenv"
        self.ANYSCALE_URL = "https://api.endpoints.anyscale.com/v1/chat/completions"
        self.ANYSCALE_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"
        self.ANYSCALE_TEMPERATURE = 0.7
        self.DB_FILE = self.DATA_DIR + "db.sqlite"
        self.LOG_FILE = self.DATA_DIR + "log.txt"
        assistantService = self._createAssistantService()
        AbstractAssistantIPlugin.__init__(self, assistantService, observable)

    def _createLLM (self) -> Anyscale:
        AssistantService.loadEnvFile(self.ENV_FILE)
        AssistantService.setLoggingConfig( self.LOG_FILE )
        os.environ["ANYSCALE_API_BASE"] = self.ANYSCALE_URL
        llm = Anyscale(model=self.ANYSCALE_MODEL, temperature=self.ANYSCALE_TEMPERATURE)
        return llm

    def _createRetriever (self) -> ColBERTv2:
        retriever = dspy.ColBERTv2(url='http://20.102.90.50:2017/wiki17_abstracts')
        return retriever

    def _createAssistant(self ) -> Assistant:
        llm = self._createLLM()
        retriever = self._createRetriever()
        agent = DSPyAssistant(llm, retriever )
        return agent

    def _createAssistantService(self) -> AssistantService:
        assistant = self._createAssistant()
        assistantService = DbAssistantService( assistant, self.DB_FILE )
        return assistantService

class SearchQueryGenerator(dspy.Signature):
    """Write a simple search query that will help answer a complex question."""

    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField()
    query = dspy.OutputField()


class AnswerGenerator(dspy.Signature):
    """Answer questions with short factoid answers."""

    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")


class MultiHopModel(dspy.Module):
    def __init__(self, passages_per_hop=3, max_hops=2):
        super().__init__()

        self.queryGenerator = [dspy.ChainOfThought(SearchQueryGenerator) for _ in range(max_hops)]
        self.retriever = dspy.Retrieve(k=passages_per_hop)
        self.answerGenerator = dspy.ChainOfThought(AnswerGenerator)
        self.max_hops = max_hops

    def forward(self, question):
        context = []

        for hop in range(self.max_hops):
            query = self.queryGenerator[hop](context=context, question=question).query
            passages = self.retriever(query).passages
            context = deduplicate(context + passages)

        pred = self.answerGenerator(context=context, question=question)
        return dspy.Prediction(context=context, answer=pred.answer)


class ZeroShotModel(dspy.Module):
    """
    Provide answer to question
    """
    def __init__(self):
        super().__init__()
        self.prog = dspy.Predict("question -> answer")

    def forward(self, question):
        return self.prog(question= question)