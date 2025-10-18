import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QListWidget, QListWidgetItem, QLabel
)
from PyQt6.QtCore import Qt, QByteArray
from PyQt6.QtGui import QPixmap

from player_backend import PlayerBackend
from api import CustomAPI
from presence import DiscordPresence
import requests

DISCORD_CLIENT_ID = '1429113771221061804'

class MainWindow(QMainWindow):
    """The main application window."""
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Nekoir3 Core")
        self.setGeometry(100, 100, 850, 600)

        self.api = CustomAPI()
        self.presence = DiscordPresence(DISCORD_CLIENT_ID)
        self.presence.connect()
        self.current_track_info = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        sec_wid = QWidget()
        sec_layout = QHBoxLayout(sec_wid)
        self.setStyleSheet("background: #362446;")

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setFixedWidth(300)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for music...")
        self.search_button = QPushButton("Search")
        self.search_results = QListWidget()

        search_box = QHBoxLayout()
        search_box.addWidget(self.search_input)
        search_box.addWidget(self.search_button)
        left_layout.addLayout(search_box)
        left_layout.addWidget(self.search_results)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        self.play_pause_button = QPushButton("▶ Play")
        self.stop_button = QPushButton("■ Stop")

        controls_layout.addStretch()
        controls_layout.addWidget(self.play_pause_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addStretch()

        right_layout.addWidget(controls_widget)

        self.image_label = QLabel("Loading Image...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(1, 1)

        self.image_url = "https://nekomimi.tilde.team/pool/05/nekoir.png"
        self.image_data = self._download_image(self.image_url)
        self.resizeEvent = self.on_resize

        if self.image_data:
            self._update_image_display()

        sec_layout.addWidget(left_panel)
        sec_layout.addWidget(self.image_label)
        main_layout.addWidget(sec_wid)
        main_layout.addWidget(right_panel)

        self.player_backend = PlayerBackend()
        self.player_backend.playback_started_callback = self.on_playback_started
        self.player_backend.playback_stopped_callback = self.on_playback_stopped


        self.search_button.clicked.connect(self.perform_search)
        self.search_input.returnPressed.connect(self.perform_search)
        self.search_results.itemDoubleClicked.connect(self.play_selected_track)
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.stop_button.clicked.connect(self.stop_playback)






    def _download_image(self, url):
        """Downloads image data from a URL synchronously."""
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(url, "Image downloaded successfully.")
                return response.content
            else:
                self.image_label.setText(f"Error: Could not load image (Status {response.status_code}).")
                return None
        except requests.exceptions.RequestException as e:
            self.image_label.setText(f"Error: Network request failed: {e}")
            return None

    def _update_image_display(self):
        """Scales and updates the QLabel's pixmap based on its current size."""
        if not self.image_data:
            return

        label_size = self.image_label.size()
        width = label_size.width()
        height = label_size.height()

        if width <= 0 or height <= 0:
            return

        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(self.image_data))

        if pixmap.isNull():
            self.image_label.setText("Error: Invalid image data.")
            return

        scaled_pixmap = pixmap.scaled(
            width,
            height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # 4. Set the scaled pixmap on the label
        self.image_label.setPixmap(scaled_pixmap)

    def on_resize(self, event):
        """Called when the window is resized."""
        super().resizeEvent(event)
        self._update_image_display()








    def perform_search(self):
        """Executes a search and populates the results list."""
        query = self.search_input.text()
        if not query:
            return

        results = self.api.search(query)
        self.search_results.clear()

        for track in results:
            item_text = f"{track['title']}\n{track['artist']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, track)
            self.search_results.addItem(item)

    def play_selected_track(self, item: QListWidgetItem):
        """Plays the track associated with the selected list item."""
        track_info = item.data(Qt.ItemDataRole.UserRole)
        if not track_info:
            return

        self.current_track_info = track_info
        track_url = self.api.get_track_url(track_info['id'])

        print(f"Playing URL: {track_url}")

        self.image_url = track_info["cover"]
        self.image_data = self._download_image(self.image_url)

        if self.image_data:
            self._update_image_display()

        self.player_backend.play_url(track_url)

    def toggle_play_pause(self):
        """Toggles the player's pause state, but for now just handles play from stopped."""
        current_state = self.player_backend.get_state()

        if current_state == 'stopped' and self.search_results.count() > 0:
            self.play_selected_track(self.search_results.item(0))
        elif current_state == 'playing':
            self.stop_playback()

    def stop_playback(self):
        """Stops playback entirely."""
        self.player_backend.stop()

    def on_playback_started(self):
        """Handles the player starting to play."""
        self.play_pause_button.setText("■ Stop") # Use 'Stop' since we only have play/stop
        if self.current_track_info:
            self.presence.update(self.current_track_info, playing=True)

    def on_playback_stopped(self):
        """Handles the player stopping or reaching the end."""
        self.play_pause_button.setText("▶ Play")
        self.presence.clear()
        self.current_track_info = None

    def closeEvent(self, event):
        """Cleanly shuts down resources when the application is closed."""
        print("Closing application...")
        self.presence.disconnect()

        # --- ffpyplayer Implementation ---
        self.player_backend.shutdown() # Ensure the ffpyplayer thread is terminated
        # --- END ffpyplayer Implementation ---

        super().closeEvent(event)

if __name__ == '__main__':
    # The locale fix for MPV is not needed for VLC.
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

