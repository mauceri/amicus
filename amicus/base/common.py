from datetime import datetime
from typing import Tuple
import os
import requests
import json
import logging
from abc import ABC, abstractmethod


class Message:
    def __init__(self, conversationId: str, speaker: str, date: str, content: str):
        self.conversationId = conversationId
        self.speaker = speaker
        self.date = date
        self.content = content


class Conversation(ABC):
    def __init__(self, id: str):
        self.id = id


class Assistant(ABC):

    @abstractmethod
    def processMessage (self,
                        inputMessage: Message,
                        conversation: Conversation) -> Tuple[Message, Conversation]:
        pass

    @abstractmethod
    def createConversation (self, conversationId: str) -> Conversation:
        pass

    @staticmethod
    def getNow() -> str:
        return datetime.now().isoformat()



class AssistantService(ABC):
    @abstractmethod
    def processMessage (self, inputMessage: Message) -> Message:
        pass

    @staticmethod
    def getNow() -> str:
        return datetime.now().isoformat()

    def setLoggingConfig(logFileFqn: str, encoding:str='utf-8', level:int=logging.DEBUG):
        logging.basicConfig(filename=logFileFqn, filemode="w", encoding=encoding, level=level)

    @staticmethod
    def loadEnvFile ( envFileFqn : str ):
        with open(envFileFqn, 'r') as file:
            for line in file:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value




