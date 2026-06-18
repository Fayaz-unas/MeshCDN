from api.discovery_api import (
    DiscoveryAPI
)

from services.peer_identity_service import (
    PeerIdentityService
)


class PeerDiscoveryService:

    @staticmethod
    def get_available_peers():

        peers = (
            DiscoveryAPI
            .get_peers()
        )

        identity = (
            PeerIdentityService
            .get_or_create_identity()
        )

        current_peer_id = (
            identity["peer_id"]
        )

        return [

            peer

            for peer in peers

            if (
                peer["peer_id"]
                != current_peer_id

                and

                peer["status"]
                == "online"
            )
        ]
