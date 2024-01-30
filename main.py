import sys
import os
import mutagen
from glob import glob
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from mutagen.flac import FLAC
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# changes QMediaPlayer backend
os.environ['QT_MULTIMEDIA_PREFERRED_PLUGINS'] = 'windowsmediafoundation'


class Player(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Musicman")
        self.icon = "assets/icon.png"
        self.setWindowIcon(QIcon(self.icon))
        self.songliststart = "Please choose an audio file."
        self.songname = self.songliststart
        self.resize(500,150)
        self.musicplayer = QMediaPlayer(self)

        # set stylesheet
        with open("stylesheet.qss", "r") as stylesheet:
            self.setStyleSheet(stylesheet.read())

        # set file directory
        with open("directory", "r") as dirfile:
            self.song_directory = dirfile.readline()
            if os.path.getsize("directory") == 0:
                self.song_directory = f"C:\\Users\{os.getlogin()}\\Music\\"

        self.createWidgets()
        self.createTray()
        self.createLayout()
        self.dirUpdate()

        # Connections
        self.customdirectory.returnPressed.connect(self.dirUpdate)
        self.customdirectoryupdate.clicked.connect(self.dirUpdate)
        self.songlistbox.activated[str].connect(self.songChange)
        self.button_play.clicked.connect(self.songPlay)
        self.button_pause.clicked.connect(self.songPause)
        self.button_min.clicked.connect(self.minimize)
        self.musicplayer.positionChanged.connect(self.positionUpdate)
        self.progressbar.sliderMoved.connect(self.progressBar)

        self.trayopen.triggered.connect(self.minimize)
        self.trayexit.triggered.connect(sys.exit)

        self.show()

    def createWidgets(self):
        self.customdirectory = QLineEdit(self.song_directory, self)
        self.customdirectoryupdate = QPushButton("Update directory", self)
        self.progressbar = QSlider(Qt.Horizontal)
        self.label = QLabel("Song selection:", self)
        self.button_play = QPushButton("Play", self)
        self.button_pause = QPushButton("", self)
        self.button_pause.setIcon(QIcon("assets/pause.png"))
        self.button_min = QPushButton("Minimize to tray", self)
        self.songlistbox = QComboBox(self)
        self.timelabel1 = QLabel("00:00", self)
        self.timelabel2 = QLabel("00:00", self)

    def createLayout(self):

        hbl = QHBoxLayout()
        hbl.addWidget(self.label)
        hbl.addWidget(self.songlistbox)

        hbl2 = QHBoxLayout()
        hbl2.addWidget(self.timelabel1)
        hbl2.addWidget(self.progressbar)
        hbl2.addWidget(self.timelabel2)

        hbl3 = QHBoxLayout()
        hbl3.addWidget(self.button_play)
        hbl3.addWidget(self.button_pause)

        hbl4 = QHBoxLayout()
        hbl4.addWidget(self.customdirectory)
        hbl4.addWidget(self.customdirectoryupdate)

        vbl = QVBoxLayout()
        vbl.addLayout(hbl4)
        vbl.addLayout(hbl)
        vbl.addLayout(hbl2)
        vbl.addLayout(hbl3)
        vbl.addWidget(self.button_min)

        self.setLayout(vbl)

    def createTray(self):
        self.trayicon = QSystemTrayIcon(QIcon(self.icon))
        self.trayicon.setToolTip("Musicman")
        traymenu = QMenu()
        self.trayopen = traymenu.addAction("Open")
        self.trayexit = traymenu.addAction("Exit")
        self.trayicon.setContextMenu(traymenu)

    def dirUpdate(self):
        try:
            self.songlistbox.clear()
            self.song_directory = str(self.customdirectory.text())
            if len(self.song_directory) == 0:
                self.song_directory = f"C:\\Users\{os.getlogin()}\\Music\\"
                self.customdirectory.setText(self.song_directory)
            elif self.song_directory[-1:] != "\\":
                self.song_directory = self.song_directory + "\\"
            start = len(self.song_directory)
            songlist = [self.song_directory + self.songliststart]
            songlist = songlist + glob(self.song_directory + "*.mp3") + glob(self.song_directory + "*.wav") \
                       + glob(self.song_directory + "*.flac")
            for song in songlist:
                self.songlistbox.addItem(song[start:])
            with open("directory", "w") as dirfile:
                dirfile.write(self.song_directory)
        except UnicodeEncodeError:
            pass



    def songChange(self):
        self.songname = self.songlistbox.currentText()
        if self.songname != self.songliststart:
            self.song = self.song_directory + self.songname
        try:
            if self.song[-3:] == "mp3":
                audio = MP3(self.song)
            elif self.song[-3:] == "wav":
                audio = WAVE(self.song)
            elif self.song[-4:] == "flac":
                audio = FLAC(self.song)
            audio_info = audio.info
            self.length = int(audio_info.length)
        except mutagen.MutagenError:
            self.length = 0
        hours, mins, secs = (self.timeConv(self.length))
        hours = str(hours)
        mins = str(mins)
        secs = str(secs)
        if len(hours) == 1:
            hours = "0" + hours
        if len(mins) == 1:
            mins = "0" + mins
        if len(secs) == 1:
            secs = "0" + secs
        if hours == "00":
            self.timelabel2.setText(f"{mins}:{secs}")
        else:
            self.timelabel2.setText(f"{hours}:{mins}:{secs}")
        self.progressbar.setRange(0, self.length)
        self.progressbar.setValue(0)

    def songPlay(self):
        try:
            self.musicplayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.song)))
            self.musicplayer.play()
        except AttributeError:
            pass

    def songPause(self):
        if self.musicplayer.state() == QMediaPlayer.PlayingState:
            self.musicplayer.pause()
        else:
            self.musicplayer.play()

    def positionUpdate(self, position):
        self.position = round(position / 1000)
        hours, mins, secs = self.timeConv(self.position)
        hours = str(hours)
        mins = str(mins)
        secs = str(secs)
        if len(hours) == 1:
            hours = "0" + hours
        if len(mins) == 1:
            mins = "0" + mins
        if len(secs) == 1:
            secs = "0" + secs
        if hours == "00":
            self.timelabel1.setText(f"{mins}:{secs}")
        else:
            self.timelabel1.setText(f"{hours}:{mins}:{secs}")
        self.progressbar.setValue(self.position)

    def progressBar(self, position):
        self.musicplayer.setPosition(position * 1000)

    def minimize(self):
        if self.isVisible():
            self.trayicon.show()
            self.hide()
        else:
            self.trayicon.hide()
            self.show()

    def timeConv(self, length):
        hours = int(length / 3600)
        minutes = int(length / 60 - hours * 60)
        seconds = round(length - hours * 3600 - minutes * 60)
        return hours, minutes, seconds


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = Player()
    sys.exit(app.exec_())
