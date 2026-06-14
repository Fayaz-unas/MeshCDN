from services.peer_identity_service import PeerIdentityService
from api.peer_api import PeerAPI


class RegistrationService:

    @staticmethod
    def register():

        peer_id = (
            PeerIdentityService
            .get_or_create_peer_id()
        )

        response = PeerAPI.register_peer(
            peer_id=peer_id,
            port=5000
        )

        return response