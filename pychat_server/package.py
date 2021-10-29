import json
from enum import Enum


class PackageType(Enum):
    USER_MSG = 0
    USER_JOINED = 1
    USER_LEFT = 2


class PackageContent:
    def __init__(self, msg: str):
        self._msg = msg

    def get_sender(self) -> str:
        return self._sender

    def get_msg(self) -> str:
        return self._msg

    def to_json(self) -> str:
        return json.dumps({"msg": self._msg})

    @staticmethod
    def from_json(data: str):
        obj = json.loads(data)
        return PackageContent(obj["msg"])


class Package:
    def __init__(self, type: PackageType, content: PackageContent):
        self._type = type
        self._sender = ""
        self._content = content

    def get_type(self) -> PackageType:
        return self._type

    def get_content(self) -> PackageContent:
        return self._content

    def get_sender(self):
        return self._sender

    def set_sender(self, sender: str):
        self._sender = sender

    def to_json(self) -> str:
        return json.dumps({"type": self._type.name, "sender": self._sender, "content": self._content.to_json()})

    @staticmethod
    def from_json(json_data: str | bytes):
        obj = json.loads(json_data)
        type_data = PackageType[obj["type"]]
        sender = obj["sender"]
        content_data = obj["content"]
        package = Package(type_data, PackageContent.from_json(content_data))
        package.set_sender(sender)
        return package
