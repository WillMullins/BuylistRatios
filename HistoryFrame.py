import tkinter as tk

class HistoryFrame:
    def __init__(self, root):
        self.masterframe = tk.Frame(root)
        self.masterframe.grid(row=0, column=1, sticky='nsew')

        yscrollbar = tk.Scrollbar(self.masterframe, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(self.masterframe, yscrollcommand=yscrollbar.set)
        self.listbox.grid(row=0, column=0, sticky='nsew')
        self.listbox.config(width=70)
        yscrollbar.grid(row=0, column=1, sticky='nsew')
        yscrollbar.config(command=self.listbox.yview)

        tk.Grid.columnconfigure(self.masterframe, 0, weight=1)
        tk.Grid.columnconfigure(self.masterframe, 1, weight=0)
        tk.Grid.rowconfigure(self.masterframe, 0, weight=1)

    def addcard(self, cardname, displayname, f, ckprice, tcgprice, sc):
        foil=''
        storecredit = ''
        if f:
            foil=' FOIL'
        if ckprice and tcgprice:
            if sc:
                ckprice = round(ckprice * 1.3, 2)
                ratio = str(round((ckprice)/tcgprice * 100, 2)) + '%'
                storecredit = ' (Store Credit)'
            else:
                ratio = str(round((ckprice)/tcgprice * 100, 2)) + '%'
        else:
            ratio = 'N/A'
        entry = cardname + ': ' + displayname + foil + ": CK: " + str(ckprice) + ', TCG: ' + str(tcgprice) + ', Ratio: ' + ratio + storecredit
        self.listbox.insert(0, entry)

    def get_masterframe(self):
        return self.masterframe
