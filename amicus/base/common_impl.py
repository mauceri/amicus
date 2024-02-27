from typing import Tuple
import os
import requests
import json
import logging
from amicus_interfaces.interfaces import IObserver, IObservable, IPlugin
from nio.rooms import MatrixRoom
from nio.events.room_events import RoomMessageText

from amicus.base.common import *
from amicus.base.sqlite_handler import SQLiteHandler

logger = logging.getLogger(__name__)

class ConversationServiceImpl(ConversationService):
    def __init__(self, dataConfiguration: DataConfiguration, assistant: Assistant ):
        self._dataConfiguration = dataConfiguration
        self._assistant = assistant
        self._id2conversation = dict()
        self._sqlLiteHandler = SQLiteHandler( dataConfiguration.dbFileFqn )

    def processMessage (self, inputMessage: Message) -> Message:
        conversationId = inputMessage.conversationId
        conversation = self._id2conversation.get( conversationId)
        oldConversation = self._assistant.createConversation(conversationId) if conversation is None else conversation
        assistantMessage, newConversation = self._assistant.processMessage(inputMessage, oldConversation)
        self._id2conversation[ conversationId] = newConversation
        self._.ajout_speeches( inputMessage, assistantMessage )
        return assistantMessage


class AssistantIOObserver(IObserver):
    def __init__(self,
                 assistant: Assistant,
                 observable: IObservable = None):
        self.__conversationService = ConversationServiceImpl(assistant)
        self.__observable = observable

    async def notify(self, room: MatrixRoom, event: RoomMessageText, msg: str):
        inputMessage = Message(room.room_id,
                                  event.sender,
                                  self.__conversationService.getNow(),
                                  msg)
        outputMessage = self.__conversationService.processMessage(inputMessage)

        await self.__observable.notify(room, event,
                                       outputMessage.content, None,
                                       None)

    def prefix(self):
        return "!assistant"


class AbstractAssistantIPlugin(IPlugin, ABC):
    def __init__(self,
                 assistant: Assistant,
                 observable: IObservable):
        self.__observer = AssistantIOObserver( assistant, observable)
        self.__observable = observable
        logger.info(f"********************** Observateur créé {self.__observer.prefix()}")

    def start(self):
        logger.info(f"********************** Inscripton de {self.__observer.prefix()}")
        self.__observable.subscribe(self.__observer)

    async def stop(self):
        pass



class AnyScaleLLM:
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
                    "dbFileName": o.dbFileName,
                    "logFileName": o.logFileName,
                    "llmUrl": o.llmUrl,
                    "llmModel": o.llmModel,
                    "llmApikey": o.llmApikeyEnvVar,
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
                o.get('dbFileName'),
                o.get('logFileName'),
                o.get('llmUrl'),
                o.get('llmModel'),
                o.get('llmApikey'),
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
