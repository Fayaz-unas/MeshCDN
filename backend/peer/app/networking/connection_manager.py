class ConnectionManager:

    def __init__(self):

        self.connections = {}

    def add_peer(
        self,
        peer_id: str,
        installation_id: str,
        address: tuple
    ):

        self.connections[peer_id] = {
            "installation_id": installation_id,
            "address": address
        }

        print(
            f"Peer connected: {peer_id}"
        )

    def remove_peer(
        self,
        peer_id: str
    ):

        if peer_id in self.connections:

            del self.connections[
                peer_id
            ]

            print(
                f"Peer disconnected: {peer_id}"
            )

            print(
                f"Connected Peers: "
                f"{self.connections}"
            )

    def get_peer(
        self,
        peer_id: str
    ):

        return self.connections.get(
            peer_id
        )

    def get_all_peers(
        self
    ):

        return self.connections

    def get_peer_count(
        self
    ):

        return len(
            self.connections
        )