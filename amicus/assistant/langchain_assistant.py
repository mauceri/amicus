from langchain.memory import ConversationBufferMemory, ConversationStringBufferMemory
from langchain_community.chat_models import ChatOpenAI
from langchain_core.tools import BaseTool

from amicus.base.common import *
from datetime import datetime
from typing import List
from langchain.agents import AgentExecutor, create_structured_chat_agent, ConversationalChatAgent
from langchain import hub


class AgentAssistant (Assistant):


    def __init__(self, llm: ChatOpenAI, tools: List[BaseTool], verbose: bool):
        self._llm = llm
        self._tools = tools
        prompt = hub.pull("hwchase17/structured-chat-agent")

        # initialize agent with tools
        # Construct the JSON agent
        agent = create_structured_chat_agent(llm, tools, prompt)
        self._agent_executor = AgentExecutor(
            agent=agent, tools=tools, verbose=verbose, handle_parsing_errors=True
        )


    def __init__chat_agent(self, llm: ChatOpenAI, tools: List[BaseTool], verbose: bool):
        self._llm = llm
        self._tools = tools

        memory = ConversationBufferMemory(memory_key="chat_history")

        chat_agent = ConversationalChatAgent.from_llm_and_tools(llm=llm, tools=tools)
        self._agent_executor = AgentExecutor.from_agent_and_tools(
            agent=chat_agent,
            tools=tools,
            memory=memory,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
            verbose=True,
        )

    def processMessage(self,
                       inputSpeech: Message,
                       conversation: Conversation) -> Tuple[Message, Conversation]:
        response = self._agent_executor.invoke({"input": inputSpeech.content})
        print("response", response)
        return Message(conversation.id, "assistant", self.getNow(), response["output"])

    def createConversation(self, conversationId: str) -> Conversation:
        return Conversation(conversationId)

    def getNow(self) -> str:
        return datetime.now().isoformat()

