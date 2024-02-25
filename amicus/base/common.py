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
                 envFileName: str,
                 dbFileName : str,
                 llmUrl: str,
                 llmModel: str,
                 llmApikey: str,
                 llmTemperature: float ):
        self.dataDir = dataDir
        self.envFileName = envFileName
        self.dbFileName = dbFileName
        self.llmUrl = llmUrl
        self.llmModel = llmModel
        self.llmApikey = llmApikey
        self.llmTemperature = llmTemperature

        self.dbFileFqn = self.dataDir + "/" + dbFileName
        envFileFqn = self.dataDir + "/" + envFileName
        self.loadEnvVariables(envFileFqn)
        self.llmApikey = llmApikey

    def setLoggingConfig(self, logFileName: str, encoding:str='utf-8', level:int=logging.DEBUG):
        logFileFqn =  self.dataDir + "/" + logFileName
        logging.basicConfig(filename=logFileFqn, filemode="w", encoding=encoding, level=level)

    @staticmethod
    def loadEnvVariables(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)



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






