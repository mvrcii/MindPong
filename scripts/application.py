import os
import platform
import time
import tkinter as tk
# import AppKit
import winsound
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *

import matplotlib
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from scripts.config import *
from scripts.pong.main import MindPong, Playing

matplotlib.use("TkAgg")
LARGE_FONT = ("Verdana", 16)
style.use("ggplot")

def play_sound():
    current_os = platform.system()
    if current_os == 'Darwin':  # Mac Beep
        pass
        # AppKit.NSBeep()  # BeepTon Mac
    elif current_os == 'Linux':  # Linux Beep
        os.system('play -nq -t alsa synth {} sine {}'.format(1500, 1500))
    elif current_os == 'Windows':  # Microsoft Beep
        winsound.Beep(1500, 1500)


class App(tk.Tk):
    # __init__ function for class App
    def __init__(self, *args, **kwargs):

        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)

        # window settings
        tk.Tk.wm_title(self, "MindPong")
        # self.geometry("%dx%d" % (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.resizable(False, False)
        self.attributes("-fullscreen", True)

        # creating a container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # creating the graph window
        self.graph = None
        self.graph_visible = False

        # initializing frames to an empty array
        self.frames = {}
        self.mind_pong = MindPong(container, self)

        # iterating through a tuple consisting
        # of the different page layouts
        for F in (StartPage, CalibrationPageOne, CalibrationPageThree, CalibrationPageFive,
                  CalibrationPageTwo, CalibrationPageFour, MindPong):
            frame = F(container, self)

            # initializing frame of the objects given
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)
        self.update()

    # UPDATE LOOP
    def update(self):
        self.after(5, self.update)

    def show_frame(self, frame_type):
        """ Display the current frame passed as parameter"""
        frame = self.frames[frame_type]
        frame.tkraise()
        frame.focus_set()

    def toggle_graph(self):
        if self.graph_visible:
            self.graph.destroy()
            self.graph_visible = False

        elif not self.graph_visible:
            self.graph = Toplevel(self)
            self.graph_visible = True
            self.graph.title('Graph')

            f = Figure(figsize=(10, 6), dpi=100)
            a = f.add_subplot(111)

            canvas = FigureCanvasTkAgg(f, self.graph)
            canvas.draw()

            self.graph.bind('<g>', lambda event: self.toggle_graph())

            toolbar = NavigationToolbar2Tk(canvas, self.graph)
            toolbar.update()

            canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text=('''Um verwertbare EEG-Daten zu erhalten, muss die Anwendung 
        zunächst mit Timern in zwei automatisierten aufeinanderfolgenden Schritten
        kalibriert werden.\n\n\n'Space' to continue\n\n\n'G' to show the graphs'''),
                         font=LARGE_FONT)
        label.pack(fill=BOTH, expand=True)

        self.bind("<space>", lambda event: controller.show_frame(CalibrationPageOne))


class CalibrationPageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text=('''Bitte fokussieren Sie nach Ablauf des 
Timers für %s Sekunden den eingeblendeten
Punkt in der Mitte des Fenster, bis Sie einen Piepton hören''' % FOCUS_POINT_TIMER), font=LARGE_FONT)
        label.pack(fill=BOTH, expand=True)

        self.bind("<space>", lambda event: controller.show_frame(CalibrationPageTwo))


class CalibrationPageTwo(tk.Frame):
    """ Calibration page with a point in the center to focus on. """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        size = 25
        canvas = Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight(), bd=0,
                        highlightthickness=0, relief='ridge')
        canvas.pack()
        circle = canvas.create_oval(0, 0, size, size, fill='red')
        canvas.move(circle, (self.winfo_screenwidth() - size) / 2, (self.winfo_screenheight() - size) / 2)

        self.bind("<space>", lambda event: controller.show_frame(CalibrationPageThree))


class CalibrationPageThree(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text=('''Bitte schließen Sie nach Ablauf des Timers für %s 
Sekunden Ihre Augen, bis Sie einen Piep Ton hören.''' % BLACK_WINDOW_TIMER), font=LARGE_FONT)
        label.pack(fill=BOTH, expand=True)

        self.bind("<space>", lambda event: controller.show_frame(CalibrationPageFour))


class CalibrationPageFour(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg='black')

        self.bind("<space>", lambda event: controller.show_frame(CalibrationPageFive))


class CalibrationPageFive(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text=('''Kalibrierung abgeschlossen!\n
Sobald der Ball den Boden berührt \n startet das Spiel nach ein paar 
Sekunden automatisch neu.\n\n Das Spiel beginnt in Kürze!'''), font=LARGE_FONT)
        label.pack(fill=BOTH, expand=True)

        self.bind("<space>", lambda event: controller.show_frame(MindPong))


app = App()
app.bind('<g>', lambda event: app.toggle_graph())
app.bind("<Escape>", quit)
app.mainloop()
