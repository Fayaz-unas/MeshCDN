import json
import uuid
import logging

from pathlib import Path

logger = logging.getLogger(__name__)


class PeerIdentityService:

    CONFIG_PATH = Path(
        "config/peer.json"
    )

    @staticmethod
    def generate_peer_id():

        return (
            f"peer_{uuid.uuid4().hex[:12]}"
        )

    @staticmethod
    def generate_installation_id():

        return uuid.uuid4().hex

    @classmethod
    def save_identity(
        cls,
        peer_id: str,
        installation_id: str
    ):
        
        """Save peer identity to config file with error handling."""
        try:
            cls.CONFIG_PATH.parent.mkdir(
                exist_ok=True,
                parents=True
            )

        except OSError as e:
            logger.error(f"Failed to create config directory: {e}")
            raise Exception(f"Cannot create config directory: {e}")
        
        except Exception as e:
            logger.error(f"Unexpected error creating directory: {e}")
            raise Exception(f"Unexpected error creating directory: {e}")

        try:
            with open(
                cls.CONFIG_PATH,
                "w"
            ) as file:

                json.dump(
                    {
                        "peer_id": peer_id,
                        "installation_id": (
                            installation_id
                        )
                    },
                    file,
                    indent=4
                )
            logger.info(f"Identity saved successfully: {peer_id}")

        except (IOError, OSError) as e:
            logger.error(f"Failed to write identity config file: {e}")
            raise Exception(f"Failed to save identity configuration: {e}")
        
        except (TypeError, ValueError) as e:
            logger.error(f"Invalid data for JSON serialization: {e}")
            raise Exception(f"Invalid identity data: {e}")
        
        except Exception as e:
            logger.error(f"Unexpected error saving identity: {e}")
            raise Exception(f"Unexpected error saving identity: {e}")
        


    @classmethod
    def load_identity(
        cls
    ):
        """Load peer identity from config file with error handling."""
        if not cls.CONFIG_PATH.exists():
            logger.info("Identity config file not found")
            return None

        try:
            with open(
                cls.CONFIG_PATH,
                "r"
            ) as file:
                identity = json.load(file)
                logger.info("Identity loaded successfully")
                return identity
            
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted identity config file (invalid JSON): {e}")
            raise Exception(f"Identity config is corrupted: {e}. File may be damaged.")
        
        except (IOError, OSError) as e:
            logger.error(f"Failed to read identity config file: {e}")
            raise Exception(f"Cannot read identity configuration: {e}")
        
        except Exception as e:
            logger.error(f"Unexpected error loading identity: {e}")
            raise Exception(f"Unexpected error loading identity: {e}")
        



    @classmethod
    def get_or_create_identity(
        cls
    ):
        """Get existing identity or create new one with error handling."""
        try:
            identity = (
                cls.load_identity()
            )

            if identity:
                logger.info("Using existing peer identity")
                return identity
            
        except Exception as e:
            logger.warning(f"Failed to load existing identity: {e}. Creating new one.")

        try:
            identity = {
                "peer_id": (
                    cls.generate_peer_id()
                ),
                "installation_id": (
                    cls.generate_installation_id()
                )
            }

            cls.save_identity(
                peer_id=identity[
                    "peer_id"
                ],
                installation_id=identity[
                    "installation_id"
                ]
            )
            logger.info(f"New peer identity created: {identity['peer_id']}")
            return identity
        
        except Exception as e:
            logger.critical(f"Failed to create and save new identity: {e}")
            raise Exception(f"Cannot create peer identity: {e}")
        

        

    @classmethod
    def get_peer_id(
        cls
    ):

        identity = (
            cls.get_or_create_identity()
        )

        return identity[
            "peer_id"
        ]

    @classmethod
    def get_installation_id(
        cls
    ):

        identity = (
            cls.get_or_create_identity()
        )

        return identity[
            "installation_id"
        ]