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

class DbAssistantService(AssistantService):
    def __init__(self,
                 assistant: Assistant,
                 dbFileFqn: str,
                 prefix:str=None):
        self._assistant = assistant
        self._id2conversation = dict()
        self._sqlLiteHandler = SQLiteHandler( dbFileFqn )
        self.prefix = prefix

    def processMessage (self, inputMessage: Message) -> Message:
        conversationId = inputMessage.conversationId
        conversation = self._id2conversation.get( conversationId)
        oldConversation = self._assistant.createConversation(conversationId) if conversation is None else conversation
        assistantMessage, newConversation = self._assistant.processMessage(inputMessage, oldConversation)
        self._id2conversation[ conversationId] = newConversation
        self._sqlLiteHandler.addMessages( inputMessage, assistantMessage )
        return assistantMessage


class AssistantIObserver(IObserver):
    def __init__(self,
                 assistantService: AssistantService,
                 observable: IObservable = None,
                 prefix: str="!assistant"):
        self._assistantService = assistantService
        self._observable = observable
        self.prefix = prefix
        

    async def notify(self, room: MatrixRoom, event: RoomMessageText, msg: str):
        inputMessage = Message(room.room_id,
                                  event.sender,
                                  self._assistantService.getNow(),
                                  msg)
        outputMessage = self._assistantService.processMessage(inputMessage)

        await self._observable.notify(room, event,
                                       outputMessage.content, None,
                                       None)

    def notify_sync(self, room: MatrixRoom, event: RoomMessageText, msg: str):
        inputMessage = Message(room.room_id,
                               event.sender,
                               self._assistantService.getNow(),
                               msg)
        outputMessage = self._assistantService.processMessage(inputMessage)

        self._observable.notify(room, event,
                                      outputMessage.content, None,
                                      None)

    def prefix(self):
        return self.prefix


class AbstractAssistantIPlugin(IPlugin, ABC):
    def __init__(self,
                 assistantService: AssistantService,
                 observable: IObservable,
                 prefix:str=None):
        self._observer = AssistantIObserver( assistantService, observable,prefix)
        self._observable = observable
        logger.info(f"********************** Observateur créé {self._observer.prefix()}")

    def start(self):
        logger.info(f"********************** Inscripton de {self._observer.prefix()}")
        self._observable.subscribe(self._observer)

    async def stop(self):
        self._observable.unsubscribe(self._observer)


