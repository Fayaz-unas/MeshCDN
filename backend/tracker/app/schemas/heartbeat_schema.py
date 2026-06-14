from pydantic import BaseModel


class HeartbeatRequest(BaseModel):
    peer_id: str