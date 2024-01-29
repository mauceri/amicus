from typing import Tuple
import os
import requests
import json
import logging

from amicus.base.common import *
from amicus.base.sqlite_handler import SQLiteHandler


class ConversationServiceImpl(ConversationService):
    def __init__(self, dataConfiguration: DataConfiguration, assistant: Assistant ):
        self.dataConfiguration = dataConfiguration
        self.assistant = assistant
        self.id2conversation = dict()
        self.sqlLiteHandler = SQLiteHandler( dataConfiguration.dbFileFqn )

    def processSpeech ( self, inputSpeech: Speech ) -> Speech:
        conversationId = inputSpeech.conversationId
        conversation = self.id2conversation.get( conversationId)
        oldConversation = self.assistant.createConversation(conversationId) if conversation is None else conversation
        assistantSpeech, newConversation = self.assistant.processSpeech(inputSpeech, oldConversation)
        self.id2conversation[ conversationId] = newConversation
        self.sqlLiteHandler.ajout_speeches( inputSpeech, assistantSpeech )
        return assistantSpeech


class AnyScaleLLM (LLM):
    def __init__(self, dataConfiguration: DataConfiguration ):
        self.dataConfiguration = dataConfiguration
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + dataConfiguration.llmApikey
        }

    def sendMessage ( self, prompt: str, message: str, temperature: float)->str:
        messages = [ { "role":"system", "content":prompt },
                              {"role": "user", "content": message} ]
        data = { "model": self.dataConfiguration.llmModel,
                 "messages": messages,
                 "temperature": temperature }
        response = requests.post( self.dataConfiguration.llmUrl,
                                headers=self.headers,
                                data=json.dumps(data))
        r = response.json()["choices"][0]["message"]["content"]
        return r


class DataConfigurationService:
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

    def saveAsJson(self,dataConfiguration:DataConfiguration, jsonFileFqn: str):
        with open(jsonFileFqn, 'w') as f:
            json.dump(dataConfiguration, f, indent=4, cls=DataConfigurationService.Encoder)

    def loadFromJson(self, jsonFileFqn: str):
        with open(jsonFileFqn, 'r') as f:
            config = json.load(f, cls=DataConfigurationService.Decoder)
        return config
