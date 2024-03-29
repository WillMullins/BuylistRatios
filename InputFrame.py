import tkinter as tk
import json
import os
import requests
from tqdm import tqdm

class InputFrame:
    def __init__(self, root,hframe):
        self.masterframe = tk.Frame(root)
        self.masterframe.grid(row=0, column=0, sticky='nsew')
        # self.masterframe.grid_propagate(0)
        self.history = hframe
        self.data = []

        self.cardname = tk.StringVar()
        self.foil = tk.IntVar()
        self.storecredit = tk.IntVar()

        self.cardnamebox = tk.Entry(self.masterframe, textvariable=self.cardname)
        self.cardnamebox.grid(row=0, column=0)
        self.cardnamebox.focus()
        self.cardnamebox.bind('<Down>', self.selectcardname)
        root.bind('<Shift_R>', self.focuscardnamebox)

        self.possiblecards = tk.Listbox(self.masterframe, bg='#d9d9d9')
        self.possiblecards.bind('<Tab>', self.clickcardname)
        self.possiblecards.bind('<Double-Button-1>', self.clickcardname)
        self.possiblecards.bind('<space>', self.focuscardnamebox)
        for letter in 'abcdefghijklmnopqrstuvwxyz/\'':
            self.possiblecards.bind(letter, self.focuscardnamebox)

        self.cardname.trace('w',self.getcardnames)

        getsets = tk.Button(self.masterframe, text='Get Sets', command=self.getsets)
        getsets.grid(row=0, column=1)
        root.bind('<Return>', self.pressedenter)

        self.usecolnums = tk.IntVar()
        usecollectornumscheck = tk.Checkbutton(self.masterframe, text='Include Collector Numbers', variable=self.usecolnums)
        usecollectornumscheck.grid(row=0, column=2)

        yscrollbar = tk.Scrollbar(self.masterframe, orient=tk.VERTICAL)
        self.setnamebox = tk.Listbox(self.masterframe, yscrollcommand=yscrollbar.set)
        self.setnamebox.grid(row=1, column=0, sticky='nsew', columnspan=3)
        self.setnamebox.config(width=60)
        yscrollbar.grid(row=1, column=2, sticky='nsew')
        yscrollbar.config(command=self.setnamebox.yview)


        self.searchframe = tk.Frame(self.masterframe)
        self.searchframe.grid(row=2, column=0)
        searchbutton = tk.Button(self.searchframe, text="Get Prices", command=self.search)
        searchbutton.grid(row=0, column=1)
        root.bind('<Shift_L>',self.pressedleftshift)

        foilcheck = tk.Checkbutton(self.searchframe, text="Foil", variable=self.foil)
        foilcheck.grid(row=0, column=0)

        storecreditcheck = tk.Checkbutton(self.searchframe, text="Use CardKingdom Store Credit", variable=self.storecredit)
        storecreditcheck.grid(row=1, column=0, columnspan=2)

        updateprintings = tk.Button(self.masterframe, text="Update Printings", command=self.updateprintings)
        updateprintings.grid(row=3,column=0)

        updateprices = tk.Button(self.masterframe, text="Update Prices", command=self.updateprices)
        updateprices.grid(row=4, column=0)

        # lightningbolt = tk.Button(self.masterframe, text="Lightning Bolt", command=lambda: self.getsets("Lightning Bolt"))
        # lightningbolt.grid(row=3, column=0)
        #
        # lovestruckbeast = tk.Button(self.masterframe, text="Elesh Norn, Mother of Machines", command=lambda: self.getsets("Elesh Norn, Mother of Machines"))
        # lovestruckbeast.grid(row=4, column=0)
        #
        # expressiveiteration = tk.Button(self.masterframe, text="Expressive Iteration", command=lambda: self.getsets("Expressive Iteration"))
        # expressiveiteration.grid(row=5, column=0)
        #
        # mindrot = tk.Button(self.masterframe, text="Mind Rot", command=lambda: self.getsets("Mind Rot"))
        # mindrot.grid(row=6, column=0)
        #
        # solring = tk.Button(self.masterframe, text="Sol Ring", command=lambda: self.getsets("Sol Ring"))
        # solring.grid(row=7, column=0)

        basepath = os.getcwd()
        self.prices = open(basepath + r'\AllPrices.json', encoding='utf8')
        self.allprices = json.load(self.prices)

        basepath = os.getcwd()
        self.file = open(basepath + r'\AllPrintings.json', encoding='utf8')
        self.allcards = json.load(self.file)



    def getsets(self, name=''):
        if self.possiblecards.curselection()!=():
            if self.possiblecards.selection_get():
                self.cardname.set(self.possiblecards.selection_get())
            self.possiblecards.place_forget()

        if name == '':
            name = self.cardname.get()

        self.data = []
        found = False
        for set in self.allcards['data']:
            for card in self.allcards['data'][set]['cards']:
                if card['name'].lower() == name.lower():
                    if card.__contains__('side'):
                        if card['side']=='b':
                            continue
                    if 'paper' in card['availability']:
                        card['displayname'] = self.allcards['data'][set]['name']
                        card['tempname'] = self.allcards['data'][set]['name']
                        self.data.append(card)
                        found=True
                        # print(card['uuid'] + ' - ' + allcards['data'][set]['name'])

        if not found:
            print("Could Not find Card: " + name)


        self.checklang()
        self.checkpromo()
        self.checkfullartborderless()
        self.checkfinishes()
        self.checkframeeffects()
        self.checkartists()
        self.checkbbfoil()
        self.checkartistandpromo()
        self.checkcollectornum()


        if self.usecolnums.get():
            for datum in self.data:
                datum['displayname'] = datum['displayname'] + ' - ' + datum['number']

        self.setnamebox.delete(0,tk.END)
        for datum in self.data:
            self.setnamebox.insert(tk.END, datum['displayname'])
        self.setnamebox.focus()
        self.setnamebox.select_set(0)

    def search(self):
        isfoil = self.foil.get()
        uuid = ''
        card = None
        for i in self.setnamebox.curselection():
            for c in self.data:
                if c['displayname'] == self.setnamebox.get(i):
                    card = c
        uuid = card['uuid']
        print(uuid)
        ckprice = 0
        tcgprice = 0

        for vendor in self.allprices['data'][uuid]['paper']:
            if vendor == 'cardkingdom':
                if isfoil:
                    if self.allprices['data'][uuid]['paper'][vendor]['buylist'].__contains__('foil'):
                        ckdate = self.getlatestpricedate(uuid, 'cardkingdom', 'buylist', 1)
                        ckprice = self.allprices['data'][uuid]['paper'][vendor]['buylist']['foil'][ckdate]
                    else:
                        ckdate = self.getlatestpricedate(uuid, 'cardkingdom', 'buylist', 0)
                        ckprice = self.allprices['data'][uuid]['paper'][vendor]['buylist']['normal'][ckdate]
                        isfoil = 0
                else:
                    if self.allprices['data'][uuid]['paper'][vendor]['buylist'].__contains__('normal'):
                        ckdate = self.getlatestpricedate(uuid, 'cardkingdom', 'buylist', 0)
                        ckprice = self.allprices['data'][uuid]['paper'][vendor]['buylist']['normal'][ckdate]
                    else:
                        ckdate = self.getlatestpricedate(uuid, 'cardkingdom', 'buylist', 1)
                        ckprice = self.allprices['data'][uuid]['paper'][vendor]['buylist']['foil'][ckdate]
                        isfoil = 1

            if vendor == 'tcgplayer':
                if isfoil:
                    if self.allprices['data'][uuid]['paper'][vendor]['buylist'].__contains__('foil'):
                        tcgdate = self.getlatestpricedate(uuid, 'tcgplayer', 'retail', 1)
                        tcgprice = self.allprices['data'][uuid]['paper'][vendor]['retail']['foil'][tcgdate]
                    else:
                        tcgdate = self.getlatestpricedate(uuid, 'tcgplayer', 'retail', 0)
                        tcgprice = self.allprices['data'][uuid]['paper'][vendor]['retail']['normal'][tcgdate]
                        isfoil = 0
                else:
                    if self.allprices['data'][uuid]['paper'][vendor]['buylist'].__contains__('normal'):
                        tcgdate = self.getlatestpricedate(uuid, 'tcgplayer', 'retail', 0)
                        tcgprice = self.allprices['data'][uuid]['paper'][vendor]['retail']['normal'][tcgdate]
                    else:
                        tcgdate = self.getlatestpricedate(uuid, 'tcgplayer', 'retail', 1)
                        tcgprice = self.allprices['data'][uuid]['paper'][vendor]['retail']['foil'][tcgdate]
                        isfoil = 1

        self.history.addcard(card['name'], card['displayname'], isfoil, ckprice, tcgprice,self.storecredit.get())


    def checklang(self):
        for datum in self.data:
            if self.isnotunique(datum):
                if datum['language'] == 'Japanese':
                    datum['tempname'] = datum['displayname'] + ' - Japanese'
                elif datum['language'] == 'Phyrexian':
                    datum['tempname'] = datum['displayname'] + ' - Phyrexian'
        self.reverttempnames()
        self.setdisplaynames()

    def checkpromo(self):
        for datum in self.data:
            if self.isnotunique(datum):
                if 'promoTypes' in datum:
                    if datum['promoTypes'][0] != 'boosterfun' and datum['promoTypes'][0] != 'concept':
                        datum['tempname'] = datum['displayname'] + ' - ' + datum['promoTypes'][0]
        self.reverttempnames()
        self.setdisplaynames()

    def checkfullartborderless(self):
        for datum in self.data:
            if self.isnotunique(datum):
                if datum['setCode'] != 'SLD':
                    if 'isFullArt' in datum:
                        if datum['isFullArt']:
                            datum['tempname'] = datum['displayname'] + ' - ' + 'Full Art'
                    elif datum['borderColor'] == 'borderless':
                        datum['tempname'] = datum['displayname'] + ' - ' + 'Borderless'
        self.reverttempnames()
        self.setdisplaynames()

    def checkfinishes(self):
        for datum in self.data:
            if self.isnotunique(datum):
                for fin in datum['finishes']:
                    if fin != 'foil' and fin != 'nonfoil':
                        datum['tempname'] = datum['displayname'] + ' - ' + fin
                        break

        self.reverttempnames()
        self.setdisplaynames()

    def checkframeeffects(self):
        for datum in self.data:
            if self.isnotunique(datum):
                try:
                    if "extendedart" in datum["frameEffects"]:
                        datum['tempname'] = datum['displayname'] + ' - Extended Art'

                    if "showcase" in datum["frameEffects"]:
                        datum['tempname'] = datum['displayname'] + ' - Showcase'

                    if "etched" in datum["frameEffects"]:
                        datum['tempname'] = datum['displayname'] + ' - Etched Foil'
                except:
                    pass
        self.reverttempnames()
        self.setdisplaynames()

    def checkartists(self):
        for datum in self.data:
            if self.isnotunique(datum):
                datum['tempname'] = datum['displayname'] + ' - ' + datum['artist']
        self.reverttempnames()
        self.setdisplaynames()

    def checkbbfoil(self):
        for datum in self.data:
            if self.isnotunique(datum):
                if datum['hasFoil'] and not datum['hasNonFoil']:
                    datum['tempname'] = datum['displayname'] + ' Foil'
        self.reverttempnames()
        self.setdisplaynames()

    def checkartistandpromo(self):
        for datum in self.data:
            if self.isnotunique(datum):
                if datum['language'] == 'Phyrexian':
                    datum['tempname'] = datum['displayname'] + ' - Phyrexian'
        for datum in self.data:
            if self.isnotunique(datum):
                if datum.__contains__('promoTypes') and datum['language'] == 'English':
                    datum['tempname'] = datum['displayname'] + ' - ' + datum['artist']
        for datum in self.data:
            if self.isnotunique(datum):
                if datum.__contains__('promoTypes'):
                    for promo in datum['promoTypes']:
                        if promo != 'boosterfun' and promo != 'concept':
                            datum['tempname'] = datum['tempname'] + ', ' + promo

        self.reverttempnames()
        self.setdisplaynames()
        for datum in self.data:
            if self.isnotunique(datum):
                if datum['language'] == 'English':
                    datum['tempname'] = datum['displayname'] + ' - ' + datum['artist']
        self.reverttempnames()
        self.setdisplaynames()

    def checkcollectornum(self):
        for datum in self.data:
            if self.isnotunique(datum):
                datum['tempname'] = datum['displayname'] + ' - ' + datum['number']
        self.reverttempnames()
        self.setdisplaynames()


    def reverttempnames(self):
        names = [d['tempname'] for d in self.data]
        revertlist = []
        for i, datum in enumerate(self.data):
            if names.count(datum['tempname']) > 1:
                revertlist.append(i)

        for i in revertlist:
            self.data[i]['tempname'] = self.data[i]['displayname']

    def setdisplaynames(self):
        for datum in self.data:
            datum['displayname'] = datum['tempname']

    def isnotunique(self, datum):
        names = [d['displayname'] for d in self.data]
        if names.count(datum['displayname']) > 1:
            return True
        return False


    def getlatestpricedate(self, uuid, vendor, type, f):
        treatment = ''
        if f:
            treatment = 'foil'
        else:
            treatment = 'normal'
        lnum = [0, 0, 0]
        ldate = ''
        for date in self.allprices['data'][uuid]['paper'][vendor][type][treatment]:

            d = [int(num) for num in date.split('-')]
            if d[0]>=lnum[0] and d[1]>=lnum[1] and d[2]>lnum[2]:
                ldate = date
        print(vendor + ": " + ldate)
        return ldate

    def updateprintings(self):
        path = os.getcwd() + r'\AllPrintings.json'
        response = requests.get("https://mtgjson.com/api/v5/AllPrintings.json", stream=True)
        totalsize = int(os.path.getsize(path))
        blocksize = 1024  # 1 Kibibyte
        progressbar = tqdm(total=totalsize, unit='iB', unit_scale=True)
        with open(path,'wb') as file:
            for data in response.iter_content(blocksize):
                progressbar.update(len(data))
                file.write(data)
            progressbar.close()
        basepath = os.getcwd()
        self.file = open(basepath + r'\AllPrintings.json', encoding='utf8')
        self.allcards = json.load(self.file)
        print("Printings Updated Successfully")

    def updateprices(self):
        path = os.getcwd() + r'\AllPrices.json'
        response = requests.get("https://mtgjson.com/api/v5/AllPrices.json", stream=True)
        totalsize = int(os.path.getsize(path))
        blocksize = 1024  # 1 Kibibyte
        print(totalsize)
        progressbar = tqdm(total=totalsize, unit='iB', unit_scale=True)
        with open(path,'wb') as file:
            for data in response.iter_content(blocksize):
                progressbar.update(len(data))
                file.write(data)
            progressbar.close()
        basepath = os.getcwd()
        self.prices = open(basepath + r'\AllPrices.json', encoding='utf8')
        self.allprices = json.load(self.prices)
        print("Prices Updated Successfully")

    def getcardnames(self,*args):
        self.possiblecards.place(x=0,y=24,height=150,width=300,anchor='nw')
        self.possiblecards.lift()
        self.possiblecards.delete(0,tk.END)
        entry = self.cardname.get()
        alreadyfound = False

        if len(entry) > 2:
            for set in self.allcards['data']:
                for card in self.allcards['data'][set]['cards']:
                    if card['name'].lower().startswith(entry.lower()):
                        alreadyfound = False
                        for existingentry in self.possiblecards.get(0,tk.END):
                            if card['name'] == existingentry:
                                alreadyfound = True
                        if not alreadyfound:
                            self.possiblecards.insert(tk.END, card['name'])

        if self.possiblecards.size()==0:
            self.possiblecards.place_forget()
            self.possiblecards.delete(0, tk.END)

        if self.possiblecards.size() == 1:
            # print(self.possiblecards.get(0).lower())
            if self.possiblecards.get(0).lower()==entry.lower():
                self.possiblecards.place_forget()
                self.possiblecards.delete(0, tk.END)


    def selectcardname(self,event):
        self.possiblecards.focus()
        self.possiblecards.select_set(0)

    def clickcardname(self,event):
        self.cardname.set(self.possiblecards.selection_get())

    def focuscardnamebox(self,event):
        self.cardnamebox.focus()
        if event.keysym == 'Shift_R':
            self.cardnamebox.select_range(0,tk.END)
        elif event.keysym == 'space':
            self.cardname.set(self.cardname.get() + ' ')
        elif event.keysym == 'apostrophe':
            self.cardname.set(self.cardname.get() + '\'')
        else:
            self.cardname.set(self.cardname.get()+event.keysym)
        self.cardnamebox.icursor(tk.END)
        # print(event.keysym)

    def pressedenter(self,event):
        self.getsets()

    def pressedleftshift(self,event):
        if self.setnamebox.curselection() != ():
            self.search()
        else:
            pass
