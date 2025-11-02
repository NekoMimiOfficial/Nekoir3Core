import time
from typing import Optional
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
        self.elapsed = 0
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

        button= [{'label': 'GitHub', 'url': "https://github.com/NekoMimiOfficial/Nekoir3Core"}]

        try:
            if playing:
                self.start_time = int(time.time())
                self.rpc.update(
                    activity_type= ActivityType.LISTENING,
                    details=f"{track_info['title']}",
                    state=f"by {track_info['artist']}",
                    large_image=track_info['cover'],
                    small_image="https://nekomimi.tilde.team/pool/05/nekoir.png",
                    large_text="Playing",
                    buttons= button,

                    start= self.start_time,
                    end= self.start_time+ int(track_info['duration']),
                )
                print(f"Presence: Updated status to playing '{track_info['title']}'.")
            else:
                self.clear()
        except Exception as e:
            print(f"Presence: Failed to update status. Error: {e}")
            self.disconnect()

    def pause(self, track_info: dict):
        print("Pausing RPC")
        if self.start_time:
            self.elapsed= int(time.time()) - self.start_time
        if self.rpc:
            self.rpc.clear()
            button= [{'label': 'GitHub', 'url': "https://github.com/NekoMimiOfficial/Nekoir3Core"}]
            self.rpc.update(
                    activity_type= ActivityType.LISTENING,
                    details=f"{track_info['title']}",
                    state=f"by {track_info['artist']}",
                    large_image=track_info['cover'],
                    small_image="https://nekomimi.tilde.team/pool/05/nekoir.png",
                    buttons= button,
                    large_text="Paused",
                )

    def resume(self, track_info: dict, elapsed: int):
        self.elapsed= int(time.time()) - elapsed
        print("Resume RPC, new timestamp:", str(self.elapsed))
        if self.rpc:
            self.start_time= self.elapsed
            button= [{'label': 'GitHub', 'url': "https://github.com/NekoMimiOfficial/Nekoir3Core"}]
            self.rpc.clear()
            self.rpc.update(
                    activity_type= ActivityType.LISTENING,
                    details=f"{track_info['title']}",
                    state=f"by {track_info['artist']}",
                    large_image=track_info['cover'],
                    small_image="https://nekomimi.tilde.team/pool/05/nekoir.png",
                    large_text="Playing",

                    buttons= button,

                    start= self.start_time,
                    end= self.start_time + int(track_info["duration"])
                )

    def clear(self):
        """Clears the Discord presence status."""
        if self.connected and self.rpc:
            try:
                self.rpc.clear()
                self.start_time = None
                print("Presence: Cleared status.")
            except Exception as e:
                print(f"Presence: Error clearing status: {e}")

