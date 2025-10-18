import time
from pypresence.presence import Presence
from pypresence.types import ActivityType

class DiscordPresence:
    """
    Handles Discord Rich Presence integration using pypresence.
    Manages the connection and updates the user's "Now Playing" status.
    """
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.rpc = None
        self.connected = False
        self.start_time = None

    def connect(self):
        """
        Establishes a connection to the Discord RPC.
        It will fail gracefully if Discord is not running.
        """
        if self.connected:
            print("Presence: Already connected.")
            return

        try:
            self.rpc = Presence(self.client_id)
            self.rpc.connect()
            self.connected = True
            # self.update({'title': 'Kitty Attack', 'artist': '3R2'})
            print("Presence: Successfully connected to Discord.")
        except Exception as e:
            self.rpc = None
            self.connected = False
            print(f"Presence: Could not connect to Discord. Is the client running? Error: {e}")

    def disconnect(self):
        """Closes the connection to the Discord RPC."""
        if self.connected and self.rpc:
            try:
                self.rpc.close()
                print("Presence: Disconnected from Discord.")
            except Exception as e:
                print(f"Presence: Error while disconnecting: {e}")
        self.connected = False
        self.rpc = None

    def update(self, track_info: dict, playing: bool = True):
        """
        Updates the Discord presence with the current track information.
        
        Args:
            track_info (dict): A dictionary containing track details like 'title' and 'artist'.
            playing (bool): Whether the track is currently playing.
        """
        if not self.connected or not self.rpc:
            print("Presence: Not connected, cannot update status.")
            return

        try:
            if playing:
                self.start_time = int(time.time())
                self.rpc.update(
                    activity_type= ActivityType.LISTENING,
                    details=f"{track_info['title']}",
                    state=f"by {track_info['artist']}",
                    large_image=track_info['cover'],
                    large_text="Nekoir3 Core",

                    start= self.start_time,
                    end= self.start_time+ int(track_info['duration']),
                )
                print(f"Presence: Updated status to playing '{track_info['title']}'.")
            else:
                self.clear()
        except Exception as e:
            print(f"Presence: Failed to update status. Error: {e}")
            self.disconnect()

    def clear(self):
        """Clears the Discord presence status."""
        if self.connected and self.rpc:
            try:
                self.rpc.clear()
                self.start_time = None
                print("Presence: Cleared status.")
            except Exception as e:
                print(f"Presence: Error clearing status: {e}")

