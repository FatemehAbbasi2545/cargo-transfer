from abc import ABC
from tkinter import Tk, Frame

class BaseFrame(ABC, Frame):
    def __init__(self, container: Tk):     
        super().__init__(container)  
        self["bg"] = '#F0F0F0'