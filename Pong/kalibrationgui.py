import os
import platform

import time
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *

import matplotlib
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

matplotlib.use("TkAgg")
LARGE_FONT = ("Verdana", 18)
style.use("ggplot")

f = Figure(figsize=(10, 6), dpi=100)
a = f.add_subplot(111)

#  3 Timer in seconds
t1 = 3  # Point
t2 = 3  # Black
t3 = 3  # before Game


def beep():
    current_os = platform.system()
    if current_os == 'Darwin':  # Mac Beep
        import AppKit
        AppKit.NSBeep()  # BeepTon Mac
    elif current_os == 'Linux':  # Linux Beep
        os.system('play -nq -t alsa synth {} sine {}'.format(1500, 1500))
    elif current_os == 'Windows':  # Microsoft Beep
        import winsound
        winsound.Beep(1500, 1500)


def game1(self, parent):  # Testort1 für Game
    tk.Frame.__init__(self, parent)
    label = tk.Label(self, text="Gaaaame", font=LARGE_FONT)
    label.pack(pady=200)


def countdown(t):  # define countdown
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer)
        time.sleep(1)
        t -= 1
    beep()


def punkt(self):
    # self.show_frame(Point)
    print('Point Window - Timer start')
    countdown(t1)
    beep()
    print('Point Window - Timer ende')
    self.show_frame(KalibrierungTwo)


def animate(i):
    pass
    # dataLink = 'https://btc-e.com/api/3/trades/btc_usd?limit=2000'
    # data = urllib.request.urlopen(dataLink)
    # data = data.read().decode("utf-8")
    # data = json.loads(data)
    #
    # data = data["btc_usd"]
    # data = pd.DataFrame(data)
    #
    # buys = data[(data['type'] == "bid")]
    # buys["datestamp"] = np.array(buys["timestamp"]).astype("datetime64[s]")
    # buyDates = (buys["datestamp"]).tolist()
    #
    # sells = data[(data['type'] == "ask")]
    # sells["datestamp"] = np.array(sells["timestamp"]).astype("datetime64[s]")
    # sellDates = (sells["datestamp"]).tolist()
    #
    # a.clear()
    #
    # a.plot_date(buyDates, buys["price"])
    # a.plot_date(sellDates, sells["price"])


class Test(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="O", font=LARGE_FONT)
        label.pack(pady=200)
        button2 = ttk.Button(self, text="Beginnen", command=lambda: app.punkt())
        button2.pack(side="bottom")


def balken(self, controller, point, name):
    prog = Progressbar(self, orient=HORIZONTAL, length=600, mode='determinate')
    prog.pack()

    def balkenladen():
        i = 0
        while i < 101:
            prog['value'] = i
            app.update_idletasks()
            time.sleep(0.005)
            i += 0.25
        controller.show_frame(point)
    Button(self, text=name, command=balkenladen).pack(pady=30)


def closewindow(window):
    window.destroy()
    app.windowcheck = FALSE


class App(tk.Tk):
    windowcheck = FALSE

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # tk.Tk.iconbitmap(self, default="clienticon.ico")
        tk.Tk.wm_title(self, "MindPong")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.geometry("800x480")
        self.frames = {}

        for F in (StartPage, KalibrierungOne):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        for F in (StartPage, KalibrierungTwo):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        for F in (StartPage, KalibrierungEnde):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        for F in (StartPage, Point):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        for F in (StartPage, Black):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        for F in (StartPage, Game):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def timer(self, timer, nxt, name):    # Timer für Point und Black Screen
        print(name, ' Window - Timer start')
        countdown(timer)
        print(name, ' Window - Timer ende')
        self.show_frame(nxt)

    def game2(self):     # Testort2 für Game
        print('Game Window - Timer start')
        countdown(t3)
        print('Game Window - Game start')

    def visualwindow(self):     # Erzeuge Fenster für Visualisierung
        if app.windowcheck == FALSE:
            app.windowcheck = TRUE
            newWindow = Toplevel(self)  # Fenster Erzeugen
            newWindow.title('Visualisierte EEG-Daten')
            newWindow.geometry('600x360')
            newWindow.geometry("+%d+%d" % (810, 43))
            canvas = FigureCanvasTkAgg(f, newWindow)    # Diagram erzeugen
            canvas.draw()
            toolbar = NavigationToolbar2Tk(canvas, newWindow)
            toolbar.pack(side=TOP, fill=X)
            toolbar.update()
            canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            button2 = ttk.Button(newWindow, text='Beenden', command=lambda: closewindow(newWindow))  # Button erzeugen
            button2.pack()
            button2.pack(side='right')
            newWindow.bind('<q>', lambda event: closewindow(newWindow))


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, compound=CENTER, text=('''Um verwertbare EEG-Daten zu erhalten, muss die Anwendung 
        zunächst mit Timern in zwei automatisierten aufeinanderfolgenden Schritten
        kalibriert werden.\n\n\n'Space' zum Fortfahren\n\n\n'V' zum Anzeigen der EEG-Daten\n\n\n'Q' zum Beenden'''),
                         font=LARGE_FONT)
        label.pack(pady=110)
        button2 = ttk.Button(self, text='Beenden', command=quit)
        button2.pack(side='bottom')


class KalibrierungOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, compound=CENTER, text=('''Bitte fokussieren Sie nach Ablauf des 
Timers für %s Sekunden den eingeblendeten
Punkt in der Mitte des Fenster, bis Sie einen Piepton hören''' % t1), font=LARGE_FONT)
        label.pack(pady=140)
        button1 = ttk.Button(self, text='Beenden', command=quit)
        button1.pack(side='bottom')
        balken(self, controller, Point, 'Kalibrierung Starten')


class KalibrierungTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text=('''Bitte schließen Sie nach Ablauf des Timers für %s 
Sekunden Ihre Augen, bis Sie einen Piep Ton hören.''' % t2), font=LARGE_FONT)
        label.pack(pady=140)
        button1 = ttk.Button(self, text='Beenden', command=quit)
        button1.pack(side='bottom')
        balken(self, controller, Black, 'Weiter')


class KalibrierungEnde(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text=('''Kalibrierung abgeschlossen!\n
Sobald der Ball den Boden berührt \n startet das Spiel nach ein paar 
Sekunden automatisch neu.\n\n Das Spiel beginnt in Kürze!'''), font=LARGE_FONT)
        label.pack(pady=90)
        button1 = ttk.Button(self, text='Beenden', command=quit)
        button1.pack(side='bottom')
        balken(self, controller, Game, 'Spiel starten')


class Point(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="O", font=LARGE_FONT)
        label.pack(pady=200)
        button2 = ttk.Button(self, text='Beginnen', command=lambda: app.timer(t1, KalibrierungTwo, 'Point'))
        button2.pack(side='bottom')


class Black(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg='black')
        button2 = ttk.Button(self, text='Beginnen', command=lambda: app.timer(t2, KalibrierungEnde, 'Black'))
        button2.pack(side='bottom')


class Game(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text='Game', font=LARGE_FONT)
        label.pack(pady=200)


app = App()
app.bind('<v>', lambda event: app.visualwindow())
app.bind('<q>', lambda event: app.quit())
app.bind('<space>', lambda event: app.show_frame(KalibrierungOne))
# ani = animation.FuncAnimation(f, animate, interval=1000)
app.mainloop()
