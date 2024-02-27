from datetime import datetime
from typing import Tuple
import os
import requests
import json
import logging
from abc import ABC, abstractmethod


class DataConfiguration:
    def __init__(self,
                 dataDir : str,
                 dbFileName : str,
                 logFileName : str,
                 llmUrl: str,
                 llmModel: str,
                 llmApikey: str,
                 llmApikeyEnvVar: str,
                 llmTemperature: float ):
        self.dataDir = dataDir
        self.dbFileName = dbFileName
        self.logFileName = logFileName
        self.llmUrl = llmUrl
        self.llmModel = llmModel
        self.llmApikey = llmApikey
        self.llmApikeyEnvVar = llmApikeyEnvVar
        self.llmTemperature = llmTemperature

        self.dbFileFqn = self.dataDir + "/" + self.dbFileName
        os.environ[self.llmApikeyEnvVar] = self.llmApikey
        self.setLoggingConfig( self.logFileName )

    def setLoggingConfig(self, logFileName: str, encoding:str='utf-8', level:int=logging.DEBUG):
        logFileFqn =  self.dataDir + "/" + logFileName
        logging.basicConfig(filename=logFileFqn, filemode="w", encoding=encoding, level=level)


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


class ConversationService(ABC):
    @abstractmethod
    def processMessage (self, inputMessage: Message) -> Message:
        pass

    @staticmethod
    def getNow() -> str:
        return datetime.now().isoformat()






