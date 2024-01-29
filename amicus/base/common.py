from typing import Tuple
import os
import requests
import json
import logging

class DataConfiguration:
    def __init__(self,
                 dataDir : str,
                 envFileName: str,
                 dbFileName : str,
                 llmUrl: str,
                 llmModel: str,
                 llmApikeyEnvVar: str,
                 llmTemperature: float ):
        self.dataDir = dataDir
        self.envFileName = envFileName
        self.dbFileName = dbFileName
        self.llmUrl = llmUrl
        self.llmModel = llmModel
        self.llmApikeyEnvVar = llmApikeyEnvVar
        self.llmTemperature = llmTemperature

        self.dbFileFqn = self.dataDir + "/" + dbFileName
        envFileFqn = self.dataDir + "/" + envFileName
        self.loadEnvVariables(envFileFqn)
        self.llmApikey = os.getenv(llmApikeyEnvVar)

    def setLoggingConfig(self, logFileName: str, encoding:str='utf-8', level:int=logging.DEBUG):
        logFileFqn =  self.dataDir + "/" + logFileName
        logging.basicConfig(filename=logFileFqn, filemode="w", encoding=encoding, level=level)

    def loadEnvVariables(self,file_path):
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

    class Encoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, DataConfiguration):
                # JSON object would be a dictionary.
                return {
                    "dataDir": o.dataDir,
                    "envFileName": o.envFileName,
                    "dbFileName": o.dbFileName,
                    "llmUrl": o.llmUrl,
                    "llmModel": o.llmModel,
                    "llmApikeyEnvVar": o.llmApikeyEnvVar,
                    "llmTemperature": o.llmTemperature
                }
            else:
                # Base class will raise the TypeError.
                return super().default(o)

    class Decoder(json.JSONDecoder):
        def __init__(self, object_hook=None, *args, **kwargs):
            super().__init__(object_hook=self.object_hook, *args, **kwargs)

        def object_hook(self, o):
            decoded_config = DataConfiguration(
                o.get('dataDir'),
                o.get('envFileName'),
                o.get('dbFileName'),
                o.get('llmUrl'),
                o.get('llmModel'),
                o.get('llmApikeyEnvVar'),
                o.get('llmTemperature'),
            )
            return decoded_config

    def saveAsJson( self, jsonFileFqn: str ):
        with open(jsonFileFqn, 'w') as f:
            json.dump(self, f, indent=4, cls=DataConfiguration.Encoder)

    @staticmethod
    def loadFromJson( jsonFileFqn: str ):
        with open( jsonFileFqn, 'r') as f:
            config = json.load(f, cls=DataConfiguration.Decoder)
        return config

class Speech:
    def __init__(self, conversationId: str, speaker: str, date: str, content: str):
        self.conversationId = conversationId
        self.speaker = speaker
        self.date = date
        self.content = content


class Conversation:
    def __init__(self, id: str):
        self.id = id

class Assistant:
    def __init__(self, dataConfiguration: DataConfiguration):
        self.dataConfiguration = dataConfiguration
    def processSpeech (self,
                        inputSpeech : Speech,
                        conversation: Conversation) -> Tuple[Speech, Conversation]:
        pass

    def createConversation (self, conversationId: str) -> Conversation:
        pass


class ConversationService:
    def processSpeech ( self, inputSpeech: Speech ) -> Speech:
        pass


class LLM:
    def sendMessage ( self, prompt: str, message: str, temperature: int)->str:
        pass



