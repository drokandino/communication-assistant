from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget, QMainWindow, QPushButton, QListWidgetItem, QListWidget, QLineEdit, QLabel, QVBoxLayout, QGridLayout
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont
import sys
import sounddevice as sd
import soundfile as sf
#import speech_recognition as sr
from speech_recognition import Recognizer, AudioFile
import pyttsx3


class VoiceRecorder():
    def __init__(self, recordingDuration,  sampleRate=44100):
        self.sampleRate = sampleRate
        self.recordingDuration = recordingDuration

    def record(self):
        #Sprema (snima) broj sampleova odreden duljinom snimanja
        myrecording = sd.rec(int(self.recordingDuration * self.sampleRate), samplerate=self.sampleRate, channels=1, blocking=True)
        #sd.wait()  # Wait until recording is finished
        return  myrecording

    def writeToFile(self, recording):
        filename = "recording.wav"  # Name of the recording file
        sf.write(filename, recording, self.sampleRate)  # Save the recording to a WAV file

class SpeechToText(Recognizer):
    def __init__(self):
        super().__init__()

        self.fileName = "recording.wav"

    def createText(self):
        with AudioFile(self.fileName) as source:
            audioData = self.record(source)
            self.text = self.recognize_google(audioData)

        return self.text
    
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.fontSize = 15
        self.screenWidth = 800
        self.screenHeight = 800
        self.setStyleSheet("QWidget {font-size: " + str(self.fontSize) + "pt;}")
        self.setWindowTitle("Communicator")
        self.setFixedSize(QSize(self.screenWidth, self.screenHeight))
        self.text = ""

        self.recorder = VoiceRecorder(recordingDuration=10)
        self.textEngine = SpeechToText()

        self.speechEngine = pyttsx3.init()
        self.voices = self.speechEngine.getProperty('voices')
        self.speechEngine.setProperty('voice', self.voices[0].id)

        # labela za prikaz snimljenog teksta
        self.label = QLabel()
        self.label.setText("")
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label.setStyleSheet("QWidget {font-size: " + str(self.fontSize + 8) + "pt;}")

        # labela duljina snimanja
        self.recordTimeLabel = QLabel()
        self.recordTimeLabel.setText("Duljina snimanja:")

        # input za duljinu snimanja
        self.recordTimeinput = QLineEdit()
        self.recordTimeinput.textChanged.connect(lambda:  self.changeRecordTime(self.recordTimeinput.text()))

        # button za povecavanje sucelja
        self.plus = QPushButton("Povečaj sučelje")
        self.plus.clicked.connect(self.bigger)

        # gumb za samnjivanje sucelja
        self.minus = QPushButton("Smanji sučelje")
        self.minus.clicked.connect(self.smaller)

        # gumb za snimanje sucelja
        self.recordButton = QPushButton("Snimi zvuk!")
        self.recordButton.clicked.connect(lambda: self.startRecording(self.record, self.setText))

        # gumb za spremanje snimljene poruke
        self.savePhrase = QPushButton("Spremi poruku")
        self.savePhrase.clicked.connect(self.saveCurrentPhrase)

        #self.messagesList = QListWidget()

        #gumb za izgovaranje poruke
        self.sayButton = QPushButton("Izgovori poruku")
        self.sayButton.clicked.connect(self.speechToText)

        # gumb za brisanje poruke
        self.deleteButton = QPushButton("Izbrisi poruku")
        self.deleteButton.clicked.connect(self.deleteMessage)

        # gumb za spremanje napisane poruke
        self.saveText = QPushButton("Spremi napisanu poruku")
        self.saveText.clicked.connect(self.saveWrittenText)

        # labla za napisanu poruku
        self.writtenTextLabel = QLabel()
        self.writtenTextLabel.setText("Napisi poruku:")

        # input za napaisanu poruku
        self.writtenText = QLineEdit()

        # Tab widget za vise listi
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabPosition(QTabWidget.North)

        # liste unutar svakog taba
        self.message_list1 = QListWidget(self.tab_widget)
        self.message_list2 = QListWidget(self.tab_widget)
        self.message_list3 = QListWidget(self.tab_widget)

        self.tab_widget.addTab(self.message_list1, "Lista 1")
        self.tab_widget.addTab(self.message_list2, "Lista 2")
        self.tab_widget.addTab(self.message_list3, "Lista 3")

        # poziv funkcije za prikaz poruka u listama
        self.updateMessages()

        # definiranje layouta i dodavanje elemenata
        layout = QGridLayout()
        layout.addWidget(self.plus, 0, 0)
        layout.addWidget(self.minus, 0, 1)
        layout.addWidget(self.recordButton, 0, 2)
        layout.addWidget(self.savePhrase, 1, 2)
        layout.addWidget(self.recordTimeLabel, 1, 0)
        layout.addWidget(self.recordTimeinput, 1, 1)
        layout.addWidget(self.saveText, 2, 2)
        layout.addWidget(self.writtenTextLabel, 2, 0)
        layout.addWidget(self.writtenText, 2, 1)
        layout.addWidget(self.label, 3, 0, 4, 3)
        #layout.addWidget(self.messagesList, 7, 0, 4, 3)
        layout.addWidget(self.tab_widget, 7, 0, 4, 3)
        layout.addWidget(self.sayButton, 11, 0)
        layout.addWidget(self.deleteButton, 11, 1)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def deleteMessage(self):
        index = self.tab_widget.currentIndex()
        text = self.tab_widget.currentWidget().currentItem().text()
        with open('poruke' + str(index+1) + '.txt', 'r+') as file:
            lines = file.readlines()
            new_lines = []
            for line in lines:
                if text in line:
                    continue
                new_lines.append(line)
            file.seek(0)
            file.truncate()
            file.writelines(new_lines)
        self.updateMessages()

    def saveWrittenText(self):
        index = self.tab_widget.currentIndex()
        with open('poruke' + str(index+1) + '.txt', mode='a+') as file:
            file.write('\n' + self.writtenText.text())
            file.seek(0)
            messages = file.read()
        self.updateMessages()

    def speechToText(self):
        text = self.tab_widget.currentWidget().currentItem().text()
        self.speechEngine.say(text)
        self.speechEngine.runAndWait()

    def saveCurrentPhrase(self):
        index = self.tab_widget.currentIndex()
        with open('poruke' + str(index+1) + '.txt', mode='a+') as file:
            file.write('\n' + self.text)
            file.seek(0)
            messages = file.read()
        self.updateMessages()

    def updateMessages(self):
        self.message_list1.clear()
        self.message_list2.clear()
        self.message_list3.clear()
        try:
            with open('poruke1.txt', 'r') as file:
                messages = file.readlines()
                for message in messages:
                    if message != '\n':
                        item = QListWidgetItem(message)
                        self.message_list1.addItem(item)
        except:
            print("No file found")
            with open("poruke1.txt", "w") as f:
                pass

        try:
            with open('poruke2.txt', 'r') as file:
                messages = file.readlines()
                for message in messages:
                    if message != '\n':
                        item = QListWidgetItem(message)
                        self.message_list2.addItem(item)
        except:
            print("No file found")
            with open("poruke2.txt", "w") as f:
                pass

        try:
            with open('poruke3.txt', 'r') as file:
                messages = file.readlines()
                for message in messages:
                    if message != '\n':
                        item = QListWidgetItem(message)
                        self.message_list3.addItem(item)
        except:
            print("No file found")
            with open("poruke3.txt", "w") as f:
                pass
    def startRecording(self, record, setText):
        setText()
        QApplication.processEvents()
        record()

    def setText(self):
        self.label.setText("Started recording")
        self.label.adjustSize()


    def record(self):
        snimka = self.recorder.record()

        print("Spremanje")
        self.recorder.writeToFile(snimka)
        self.label.setText("Finished recording")
        self.text = self.textEngine.createText()
        print(self.text)
        self.label.setText(self.text)

        """     # Zakljucava gumb
        self.setEnabled(False)
        self.setEnabled(True)
        """


    def changeRecordTime(self, text):
        self.recorder = VoiceRecorder(recordingDuration=int(text))

    def smaller(self):
        self.fontSize -= 3
        self.setStyleSheet("QWidget {font-size: " + str(self.fontSize) + "pt;}")

        self.label.setStyleSheet("QWidget {font-size: " + str(self.fontSize + 8) + "pt;}")

        self.screenHeight *= 0.9
        self.screenWidth *= 0.9
        self.setFixedSize(QSize(self.screenWidth, self.screenHeight))

    def bigger(self):
        self.fontSize += 3
        self.setStyleSheet("QWidget {font-size: " + str(self.fontSize) + "pt;}")

        self.label.setStyleSheet("QWidget {font-size: " + str(self.fontSize + 8) + "pt;}")

        self.screenHeight *= 1.1
        self.screenWidth *= 1.1
        self.setFixedSize(QSize(self.screenWidth, self.screenHeight))


app = QApplication(sys.argv)

# Create a Qt widget, which will be our window.
window = MainWindow()
window.show()  # IMPORTANT!!!!! Windows are hidden by default.

# Start the event loop.
app.exec()