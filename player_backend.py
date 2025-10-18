import time
import threading
from ffpyplayer.player import MediaPlayer

class PlayerBackend:
    """
    Simplified media player backend using ffpyplayer, supporting play/stop.
    """
    def __init__(self):
        self._player = None
        self._url_cache = None
        self._state = 'stopped'

        self.playback_started_callback = None
        self.playback_stopped_callback = None

    def play_url(self, url: str):
        """Loads and starts playing a new URL."""
        self.stop()
        opts = {'vn': 1, 'reconnect': 1, 'reconnect_streamed': 1, 'reconnect_delay_max': 5}

        try:
            self._player = MediaPlayer(url, ff_opts=opts)
            self._url_cache = url

            self._monitor_thread = threading.Thread(target=self._monitor_playback, daemon=True)
            self._monitor_thread.start()

            self._state = 'playing'
            if self.playback_started_callback:
                self.playback_started_callback()

        except Exception as e:
            print(f"Error initializing ffpyplayer: {e}")
            self._player = None
            self._state = 'stopped'


    def stop(self):
        """Stops playback entirely and cleans up resources."""
        if self._player:
            print("Stopping ffpyplayer...")
            try:
                self._player.close()
            except Exception as e:
                print(f"Error closing ffpyplayer: {e}")
            finally:
                self._player = None
                self._url_cache = None

                if self._state != 'stopped':
                    self._state = 'stopped'
                    if self.playback_stopped_callback:
                        self.playback_stopped_callback()

    def _monitor_playback(self):
        """Monitors the player state and calls the stop callback on end."""
        while self._player:
            frame, val = self._player.get_frame()

            if val == 'eof':
                print("End of file reached.")
                self.stop()
                return

            if val is None and self._player is None:
                return

            time.sleep(0.1)


    def get_state(self) -> str:
        """Returns the current playback state ('playing' or 'stopped')."""
        return self._state

    def shutdown(self):
        """Ensures the player is stopped when the app closes."""
        self.stop()
