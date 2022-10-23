import json

from test.dummy_message import DummyMessage


class DummyUpdate:
    def __init__(self, chat, from_user):
        self.message = DummyMessage(chat=chat, from_user=from_user)
