from pydantic import BaseModel

class PeerRegistrationRequest(BaseModel):
    peer_id: str
    port: int
    installation_id: str
  