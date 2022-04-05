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

f = Figure(figsize=(10, 6), dpi=100)
a = f.add_subplot(111)

#  3 Timer in seconds
t1 = 0  # Point
t2 = 0  # Black
t3 = 0  # before Game


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
    windowcheck = FALSE

    # __init__ function for class App
    def __init__(self, *args, **kwargs):

        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)

        # window settings
        tk.Tk.wm_title(self, "MindPong")
        self.geometry("%dx%d" % (WINDOW_WIDTH, WINDOW_HEIGHT))

        # creating a container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.curr_timer = 0
        self.timer_label = None

        # timer variables
        self.updateCounter = 0
        self.lastUpdate = 0
        self.passedTime = 0

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

    def update(self):
        delta = self.handle_time()

        self.curr_timer += 1
        self.timer_label['text'] = self.curr_timer

        self.after(5, self.update)

    def show_frame(self, frame_type):
        """ Display the current frame passed as parameter"""
        frame = self.frames[frame_type]
        frame.tkraise()
        frame.focus_set()

    def timer(self, timer, nxt, name):  # Timer für Point und Black Screen
        print(name, ' Window - Timer start')
        self.countdown(timer)
        print(name, ' Window - Timer ende')
        self.show_frame(nxt)

    def toggle_graph(self):  # Erzeuge Fenster für Visualisierung
        if app.windowcheck == FALSE:
            app.windowcheck = TRUE
            newWindow = Toplevel(self)  # Fenster Erzeugen
            newWindow.title('Visualisierte EEG-Daten')
            newWindow.geometry('600x360')
            newWindow.geometry("+%d+%d" % (810, 43))
            canvas = FigureCanvasTkAgg(f, newWindow)  # Diagram erzeugen
            canvas.draw()
            toolbar = NavigationToolbar2Tk(canvas, newWindow)
            toolbar.pack(side=TOP, fill=X)
            toolbar.update()
            canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            button2 = ttk.Button(newWindow, text='Beenden', command=lambda: self.closewindow(newWindow))  # Button erzeugen
            button2.pack()
            button2.pack(side='right')
            newWindow.bind('<q>', lambda event: self.closewindow(newWindow))

    def handle_time(self):
        # Time control
        self.updateCounter = self.updateCounter + 1
        now = round(time.time() * 1000)

        if self.lastUpdate == 0:
            self.lastUpdate = now

        delta = now - self.lastUpdate

        self.passedTime = self.passedTime + delta

        if self.passedTime > 1000:
            print("FPS: ", self.updateCounter)
            self.updateCounter = 0
            self.passedTime = 0
        self.lastUpdate = now
        return delta

    def countdown(self, t):  # define countdown
        while t:
            mins, secs = divmod(t, 60)
            timer = '{:02d}:{:02d}'.format(mins, secs)
            print(timer)
            time.sleep(1)
            t -= 1
        play_sound()

    def punkt(self):
        print('Point Window - Timer start')
        self.countdown(t1)
        play_sound()
        print('Point Window - Timer ende')
        self.show_frame(CalibrationPageThree)

    def balken(self, controller, point, name):
        prog = Progressbar(self, orient=HORIZONTAL, length=600, mode='determinate')
        prog.pack()

        def balkenladen():
            i = 0
            while i < 101:
                prog['value'] = i
                app.update_idletasks()
                # time.sleep(0.005)
                i += 0.25
            controller.show_frame(point)

        Button(self, text=name, command=balkenladen).pack(pady=30)

    def closewindow(self, window):
        window.destroy()
        app.windowcheck = FALSE


# start frame
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text=('''Um verwertbare EEG-Daten zu erhalten, muss die Anwendung 
        zunächst mit Timern in zwei automatisierten aufeinanderfolgenden Schritten
        kalibriert werden.\n\n\n'Space' to continue\n\n\n'G' to show the graphs'''),
                         font=LARGE_FONT)
        label.pack()

        self.bind("<space>", lambda event: controller.show_frame(CalibrationPageOne))


class CalibrationPageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text=('''Bitte fokussieren Sie nach Ablauf des 
Timers für %s Sekunden den eingeblendeten
Punkt in der Mitte des Fenster, bis Sie einen Piepton hören''' % t1), font=LARGE_FONT)
        label.pack()

        self.prog = Progressbar(self, orient=HORIZONTAL, length=600, mode='determinate')
        self.prog.pack()

        controller.timer_label = tk.Label(self, text=str(controller.curr_timer))
        controller.timer_label.pack()

        controller.balken(controller, CalibrationPageTwo, 'Kalibrierung Starten')


class CalibrationPageTwo(tk.Frame):
    """ Calibration page with a point in the center to focus on. """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        size = 25
        canvas = Canvas(self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bd=0, highlightthickness=0, relief='ridge')
        canvas.pack()
        circle = canvas.create_oval(0, 0, size, size, fill='red')
        canvas.move(circle, (WINDOW_WIDTH - size) / 2, (WINDOW_HEIGHT - size) / 2)

        button2 = ttk.Button(self, text='Beginnen', command=lambda: app.timer(t1, CalibrationPageThree, 'Point'))
        button2.pack(side='bottom')


class CalibrationPageThree(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text=('''Bitte schließen Sie nach Ablauf des Timers für %s 
Sekunden Ihre Augen, bis Sie einen Piep Ton hören.''' % t2), font=LARGE_FONT)
        label.pack(pady=140)

        controller.balken(controller, CalibrationPageFour, 'Weiter')


class CalibrationPageFour(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg='black')
        button2 = ttk.Button(self, text='Beginnen', command=lambda: app.timer(t2, CalibrationPageFive, 'Black'))
        button2.pack(side='bottom')


class CalibrationPageFive(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text=('''Kalibrierung abgeschlossen!\n
Sobald der Ball den Boden berührt \n startet das Spiel nach ein paar 
Sekunden automatisch neu.\n\n Das Spiel beginnt in Kürze!'''), font=LARGE_FONT)
        label.pack()

        button1 = ttk.Button(self, text='Spiel Fenster', command=lambda: controller.start_pong())
        button1.pack(side='bottom')

        # balken(self, controller, MindPong, 'Spiel starten')


app = App()
app.bind('<g>', lambda event: app.toggle_graph())
app.bind("<Escape>", quit)
app.mainloop()
