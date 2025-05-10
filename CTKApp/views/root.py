from customtkinter import *
from .arbimon_window import ArbimonWindow
from .welcome_app import PipeSoundWelcome
from .audio_analyzer import AudioAnalyzer
from .terminal import TerminalWindow
from utils.app_logger import set_logger
from .violin_Charts_Window import ViolinChartWindow


class Root(CTk):
    def __init__(self):
        super().__init__()
        self.title("PipeSound")
        self.app_width = 1280
        self.app_height = 720
        x = (self.winfo_screenwidth() // 2) - (self.app_width // 2)
        y = (self.winfo_screenheight() // 2) - (self.app_height // 2)
        self.geometry(f"{self.app_width}x{self.app_height}+{x}+{y}")
        self.configure(fg_color="#272B2B")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.terminal = TerminalWindow(self)
        self.terminal.geometry("+50+50")

        set_logger(self.terminal.append_text)

        container = CTkFrame(self)
        container.grid(row=0, column=0, sticky="nsew")  

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (ArbimonWindow, PipeSoundWelcome, AudioAnalyzer, ViolinChartWindow):
            frame = F(parent=container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("PipeSoundWelcome")

    def show_frame(self, name: str, **kwargs):
        frame = self.frames[name]
        if kwargs:
            frame.receive_data(**kwargs)
        if name == "ArbimonWindow":
            frame.load_up()
        frame.tkraise()