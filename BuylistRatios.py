import tkinter as tk
from InputFrame import *
from HistoryFrame import *

class BuylistRatios:
    def __init__(self, root):
        tk.Grid.rowconfigure(root, 0, weight=1)
        tk.Grid.columnconfigure(root, 0, weight=0)
        tk.Grid.columnconfigure(root, 1, weight=1)
        historyframe = HistoryFrame(root)
        inputfr = InputFrame(root, historyframe)
        root.mainloop()


root = tk.Tk()
buylistratio = BuylistRatios(root)