# RT Annotator (Real Time Annotator)
# Shamoun Gergi
# Recently updated: 17-06-2021


from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QSlider, QStyle, QSizePolicy, QFileDialog, QGraphicsView, QSpacerItem, QCheckBox
import sys
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QMessageBox

import bisect
from time import *

# import random
from itertools import count
# import pandas as pd
# import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
# from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import csv


import numpy as np


class MplCanvas(FigureCanvas):
    """This class helps to create a widget/ canvas for the plotting-area. It's namely a part of the integration
    between PyQt5 and the plotting libraries"""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        # self.axes.hold(False)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

    def compute_initial_figure(self):
        pass


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RT Annotator")
        self.setGeometry(350, 100, 1080, 720)
        self.setWindowIcon(QIcon('player.png'))

        p = self.palette()
        p.setColor(QPalette.Window, Qt.white)
        self.setPalette(p)

        self.init_ui()

        self.show()

    def init_ui(self):

        # Creats two lists: one for x-values, one for y-valuse
        self.xValues = []
        self.yValues = []

        # create media player object
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        # create videowidget object
        videowidget = QVideoWidget()

        # create "open video" button
        self.openVideoBtn = QPushButton(' Open Video')
        self.openVideoBtn.clicked.connect(self.open_file)
        self.openVideoBtn.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))

        # create "open annotation" button
        self.openAnnotationBtn = QPushButton(' Open Annotation')
        self.openAnnotationBtn.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))

        # create save button
        self.saveBtn = QPushButton(' Save Annotation')
        self.saveBtn.clicked.connect(self.save_annotation)
        self.saveBtn.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.saveBtn.setEnabled(False)

        # creat reset button
        self.resetBtn = QPushButton(" Clear Annotation")
        self.resetBtn.clicked.connect(self.reset_annotation)
        self.resetBtn.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))

        # create button for playing
        self.playBtn = QPushButton()
        self.playBtn.setEnabled(False)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.clicked.connect(self.play_video)

        # create button for stop
        self.stopBtn = QPushButton()
        self.stopBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stopBtn.clicked.connect(self.stop_video)

        # create button for record
        self.recordLabel = QLabel("Record: ")
        self.recordLabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.checkbox = QCheckBox()

        # create slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        # create numLabel. This will review the value of
        self.numLabel = QLabel("%")
        self.numLabel.setStyleSheet("background-color: white")
        self.numLabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Create vertical slider
        self.VerticalSlider = QSlider(Qt.Vertical)
        self.VerticalSlider.sliderMoved['int'].connect(self.numLabel.setNum)

        # create label
        self.label = QLabel()
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # create spacer
        spacerItem = QSpacerItem(128, 17, QSizePolicy.Expanding, QSizePolicy.Minimum)

        ###############################d#############################################################################
        ############################################################################################################

        # Create a canvas for the diagram, using the MplCanvas-class above.
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)

        # Defining the x and y axis:
        self.x = np.linspace(0, 100, 10)
        self.y = np.linspace(0, 100, 10)
        self.line, = self.canvas.axes.plot(self.x, self.y, animated=True, lw=2)
        self.pointer, = self.canvas.axes.plot(self.x, self.y, animated=True, lw=2)



        self.index = count()

        # self.ax = plt.subplots(figsize=(5, 4), dpi=200)

        ###############################d#############################################################################
        ############################################################################################################

        # Layout

        # create hbox layout (upper horizontal box).
        upper_hbox = QHBoxLayout()
        upper_hbox.setContentsMargins(0, 0, 0, 0)

        # set widgets to the hbox layout
        upper_hbox.addWidget(self.numLabel)
        # upper_hbox.addWidget(toolbar)
        upper_hbox.addWidget(self.openVideoBtn)
        upper_hbox.addWidget(self.openAnnotationBtn)
        upper_hbox.addWidget(self.saveBtn)
        upper_hbox.addItem(spacerItem)
        upper_hbox.addWidget(self.resetBtn)

        # ---------------------------------------------------------------------------------------

        # create hbox layout (middle horizontal box).
        middle_hbox = QHBoxLayout()
        middle_hbox.setContentsMargins(0, 0, 0, 0)

        # set widgets to the hbox layout
        middle_hbox.addWidget(self.VerticalSlider)
        middle_hbox.addWidget(self.canvas)
        middle_hbox.addWidget(videowidget)

        # ---------------------------------------------------------------------------------------

        # create hbox layout (lower horizontal box).
        lower_hbox = QHBoxLayout()
        lower_hbox.setContentsMargins(0, 0, 0, 0)

        # set widgets to the hbox layout
        lower_hbox.addWidget(self.playBtn)
        lower_hbox.addWidget(self.stopBtn)
        lower_hbox.addWidget(self.recordLabel)
        lower_hbox.addWidget(self.checkbox)
        lower_hbox.addWidget(self.slider)

        # ---------------------------------------------------------------------------------------

        # create vbox layout (vertical box)
        vboxLayout = QVBoxLayout()
        vboxLayout.addLayout(upper_hbox)
        vboxLayout.addLayout(middle_hbox)
        vboxLayout.addLayout(lower_hbox)

        self.setLayout(vboxLayout)

        self.mediaPlayer.setVideoOutput(videowidget)

        # ---------------------------------------------------------------------------------------

        # media player signals

        self.mediaPlayer.stateChanged.connect(self.mediastate_changed)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

    def update_line(self, i):
        # print( time()- self.startTime)
        # print(self.slider.value())
        print(self.mediaPlayer.position(), " ms \t \t", self.VerticalSlider.value(), " %")

        # self.xValues.append(next(self.index))
        # self.xValues.append(1)
        if self.checkbox.isChecked():

            current_position = self.mediaPlayer.position()


            if self.xValues == []:
                # "If the list of xValues is empty". This happens only in the start of the plotting process.
                self.xValues.append(current_position)
                self.yValues.append(self.VerticalSlider.value())

            if self.xValues != []:

                if current_position > max(self.xValues):
                    # "If the point is bigger than the last point". I.e if the point will be plotted in the end of the current graph.

                    self.xValues.append(current_position)
                    self.yValues.append(self.VerticalSlider.value())

                if current_position < max(self.xValues):
                    # "If the point is smaller than the last point". I.e if the point will be plotted in the middle of the current graph.

                    bisect.insort(self.xValues,
                                  current_position)  # Through this method, the element is inserted in order.
                    self.yValues.insert(self.xValues.index(current_position), self.VerticalSlider.value())

                    position_index = self.xValues.index(current_position)
                    # if position_index != -1:
                    # If the element is not the last element. Becuase the last element doesen't have "index + 1".


                    if current_position == 0:
                        current_position = 10
                        self.set_position(10)
                        # This if-statement solves a bug. The program has a problem when the current position is 0.


                    if self.xValues[position_index + 1] - current_position < 100:

                        if position_index < (len(self.xValues) - 1):
                            self.xValues.pop(position_index + 1)
                            self.yValues.pop(position_index + 1)

                            if position_index < (len(self.xValues) - 2):
                                self.xValues.pop(position_index + 2)
                                self.yValues.pop(position_index + 2)

                        # print(self.xValues)

        self.line, = self.canvas.axes.plot(self.xValues, self.yValues, '#ff000b')

        self.show()

        return [self.line]

    def update_pointer(self, i):

        self.pointer, = self.canvas.axes.plot([self.slider.value()], [self.VerticalSlider.value()], '#1dff00')
        self.show()
        return [self.pointer]

    def open_file(self):
        self.filename, _ = QFileDialog.getOpenFileName(self, "Open Video")

        if self.filename != '':
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.filename)))
            self.playBtn.setEnabled(True)
            self.saveBtn.setEnabled(True)
            print(self.filename)

    def play_video(self):
        self.startTime = time()
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            self.ani._stop()


            self.checkbox.setEnabled(True)
            self.saveBtn.setEnabled(True)
            self.openVideoBtn.setEnabled(True)
            self.openAnnotationBtn.setEnabled(True)
            self.resetBtn.setEnabled(True)


        else:
            self.mediaPlayer.play()
            self.y = np.linspace(0, self.mediaPlayer.duration(), 10)
            self.ani = FuncAnimation(self.canvas.figure, self.update_line, blit=True, interval=10)

            self.checkbox.setEnabled(False)
            self.saveBtn.setEnabled(False)
            self.openVideoBtn.setEnabled(False)
            self.openAnnotationBtn.setEnabled(False)
            self.resetBtn.setEnabled(False)


    def stop_video(self):
        print(self.xValues)
        self.checkbox.setEnabled(True)
        self.saveBtn.setEnabled(True)
        self.openVideoBtn.setEnabled(True)
        self.openAnnotationBtn.setEnabled(True)
        self.resetBtn.setEnabled(True)


        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.stop()
            self.ani._stop()
            self.checkbox.setEnabled(True)

        if self.mediaPlayer.state() == QMediaPlayer.PausedState:
            self.mediaPlayer.stop()
            self.checkbox.setEnabled(True)
        else:
            pass

    def reset_annotation(self):
        self.xValues = []
        self.yValues = []
        self.stop_video()

    def mediastate_changed(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playBtn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause)

            )

        else:
            self.playBtn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay)

            )

    def position_changed(self, position):
        self.slider.setValue(position)

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)


    def save_annotation(self):
        with open(self.filename.replace(".mp4",".csv"), "w", newline="\n") as file:
            writer = csv.writer(file)
            writer.writerow(["Time (ms)", "Engagement (%)"])

            for n in range(len(self.xValues)):
                writer.writerow([self.xValues[n], self.yValues[n]])

        message = QMessageBox()
        message.setWindowTitle("Success!")
        message.setText("The annotation is saved successfully as a csv-file. It is saved as the same directory as the sourse video file.")
        x = message.exec_()  # this will show our messagebox


    def handle_errors(self):
        self.playBtn.setEnabled(False)
        self.label.setText("Error: " + self.mediaPlayer.errorString())


app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec_())