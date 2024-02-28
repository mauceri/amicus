from langchain_community.chat_models import ChatAnyscale
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import  BaseTool, StructuredTool, tool
from typing import Optional, Type
from langchain_core.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from amicus.base.common import *
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Anyscale
from os.path import dirname, abspath
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain import hub

class CalculatorInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")


class CustomCalculatorTool(BaseTool):
    name = "Calculator"
    description = "useful for when you need to answer questions about math"
    args_schema: Type[BaseModel] = CalculatorInput
    return_direct: bool = True

    def _run(
            self, a: int, b: int, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        return a * b

    async def _arun(
            self,
            a: int,
            b: int,
            run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Calculator does not support async")


REPERTOIRE_BASE = dirname(dirname(abspath(__file__)))
REPERTOIRE_DATA = REPERTOIRE_BASE + "/data_tests"
ANYSCALE_API_BASE  = "https://api.endpoints.anyscale.com/v1/chat/completions"
ANYSCALE_MODEL_NAME = "mistralai/Mixtral-8x7B-Instruct-v0.1"

os.environ["ANYSCALE_API_KEY"] = ANYSCALE_API_KEY
os.environ["ANYSCALE_API_BASE "] = ANYSCALE_API_BASE


llm =  ChatAnyscale(model_name=ANYSCALE_MODEL_NAME)

tools = [ CustomCalculatorTool()]
prompt = hub.pull("hwchase17/structured-chat-agent")

# initialize agent with tools
# Construct the JSON agent
agent = create_structured_chat_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
)

response = agent_executor.invoke({"input": "can you calculate the multiplication of 10 and 12?"})

print( "response", response)
