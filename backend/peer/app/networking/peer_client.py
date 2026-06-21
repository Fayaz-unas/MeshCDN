import socket


class PeerClient:

    def __init__(
        self
    ):
        self.client = None

    def connect(
        self,
        host: str,
        port: int
    ):
        """Connect to a peer server."""
        try:
            self.client = socket.socket()
            self.client.connect(
                (
                    host,
                    port
                )
            )
            print(f"✅ Connected to {host}:{port}")

        except socket.gaierror as e:
            print(f"❌ Invalid host/port: {e}")
            raise Exception(f"Cannot connect to {host}:{port}: Invalid address")
        
        except socket.timeout as e:
            print(f"❌ Connection timeout to {host}:{port}: {e}")
            raise Exception(f"Connection timeout: {host}:{port}")
        
        except ConnectionRefusedError as e:
            print(f"❌ Connection refused by {host}:{port}: {e}")
            raise Exception(f"Peer not responding: {host}:{port}")
        
        except Exception as e:
            print(f"❌ Failed to connect to {host}:{port}: {e}")
            raise

    def send_message(
        self,
        message: str
    ):
        """Send message to connected peer."""
        try:
            if not self.client:
                raise Exception("Not connected to any peer")
            self.client.send(
                message.encode()
            )
            print(f"📤 Message sent: {message[:50]}")

        except AttributeError as e:
            print(f"❌ Socket error: {e}")
            raise Exception("Connection closed unexpectedly")
        
        except BrokenPipeError as e:
            print(f"❌ Peer disconnected: {e}")
            raise Exception("Peer disconnected")
        
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            raise

    def receive_message(
        self
    ):
        """Receive message from connected peer."""
        try:
            if not self.client:
                raise Exception("Not connected to any peer")
            data = self.client.recv(
                1024
            )
            if not data:
                print("⚠️  Received empty data from peer")
                return None
            message = data.decode()
            print(f"📥 Message received: {message[:50]}")
            return message
        
        except socket.timeout as e:
            print(f"⚠️  Receive timeout: {e}")
            raise Exception("Receive timeout")
        
        except UnicodeDecodeError as e:
            print(f"❌ Failed to decode message: {e}")
            raise Exception("Invalid message format")
        
        except Exception as e:
            print(f"❌ Failed to receive message: {e}")
            raise

    def disconnect(
        self
    ):
        """Disconnect from peer server."""
        try:
            if self.client:
                self.client.close()
                print("✅ Disconnected from peer")
                self.client = None
                
        except Exception as e:
            print(f"❌ Error during disconnect: {e}")
            self.client = None