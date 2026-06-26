import json


class MessageTypes:

    HELLO = "HELLO"
    WELCOME = "WELCOME"

    PING = "PING"
    PONG = "PONG"

    REQUEST_CHUNK = "REQUEST_CHUNK"

    CHUNK_DATA = "CHUNK_DATA"

    CHUNK_NOT_FOUND = "CHUNK_NOT_FOUND"


class Protocol:

    @staticmethod
    def create_message(
        message_type: str,
        payload: dict | None = None
    ) -> str:

        return json.dumps(
            {
                "type": message_type,
                "payload": payload or {}
            }
        )

    @staticmethod
    def parse_message(
        message: str
    ) -> dict:

        return json.loads(
            message
        )

    @staticmethod
    def get_type(
        message: dict
    ) -> str:

        return message["type"]

    @staticmethod
    def get_payload(
        message: dict
    ) -> dict:

        return message["payload"]