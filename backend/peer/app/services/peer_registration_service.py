from services.peer_identity_service import PeerIdentityService
from api.registration_api import RegistrationAPI 
from services.settings_service import SettingsService

port = SettingsService.get_peer_port()

class RegistrationService:

    @staticmethod
    def register():

        identity = (
            PeerIdentityService
            .get_or_create_identity()
        )

        peer_id = identity["peer_id"]
        installation_id = identity["installation_id"]

        response = RegistrationAPI.register_peer(
            peer_id=peer_id,
            installation_id=installation_id,
            port=port
            
        )

        return response