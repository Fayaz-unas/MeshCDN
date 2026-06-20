import logging
import threading

logger = logging.getLogger(__name__)


class ConnectionManager:
   

    def __init__(self):
        self.connections = {}
        self.lock = threading.Lock()
        logger.info("ConnectionManager initialized")

    def add_peer(self, 
            peer_id: str,
            installation_id: str,
            address: tuple
            ):
        
        try:
            with self.lock:
                self.connections[peer_id] = {
                    "installation_id": installation_id,
                    "address": address
                }
            logger.info(f"Peer added: {peer_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to add peer {peer_id}: {e}")
            return False

    def remove_peer(
            self, 
            peer_id: str
        ):
       
        try:
            with self.lock:
                if peer_id in self.connections:
                    del self.connections[peer_id]
                    logger.info(f"Peer removed: {peer_id}")
                    return True
                
            logger.warning(f"Peer not found: {peer_id}")
            return False
        
        except Exception as e:
            logger.error(f"Failed to remove peer {peer_id}: {e}")
            return False

            
    def get_peer(
            self,
            peer_id: str
        ):
        
        try:
            with self.lock:
                return self.connections.get(peer_id)
            

        except Exception as e:
            logger.error(f"Failed to get peer {peer_id}: {e}")
            return None

    def get_all_peers(self):
       
        try:
            with self.lock:
                return  self.connections
            
        except Exception as e:
            logger.error(f"Failed to get all peers: {e}")
            return {}

    def get_peer_count(self):
        
        try:
            with self.lock:
                return len(self.connections)
            
        except Exception as e:
            logger.error(f"Failed to get peer count: {e}")
            return 0