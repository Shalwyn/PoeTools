import tkinter as tk
from tkinter import filedialog
from tkinter import Tk, END
import re
import json
import requests
import threading
from pynput.keyboard import Key, Controller
import sys
if sys.platform == "linux":
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("Wnck", "3.0")
    from gi.repository import Gtk, Gdk, Wnck
else:
    import pygetwindow as gw
import webbrowser
import os
import subprocess
import time
from tkinter.colorchooser import askcolor
import configparser

config = configparser.ConfigParser()
if sys.platform == "linux":
    config.read('{}/config.ini'.format(os.getcwd()))
else:
    config.read('{}\config.ini'.format(os.getcwd()))

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


def buyitem(whisper):
    if sys.platform == "linux":
        subprocess.Popen("wmctrl -a Path of Exile", stdout=subprocess.PIPE, shell=True)
    else:
        notepadWindow = gw.getWindowsWithTitle('Path of Exile')[0]
        notepadWindow.activate()

    time.sleep(1)

    keyboard = Controller()
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
    keyboard.type(u'\u0040')
    time.sleep(0.1)
    keyboard.type(whisper[1:])
    time.sleep(0.1)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)




def searchwindowset():
    class CreateToolTip(object):

        def __init__(self, widget, text='widget info'):
            self.widget = widget
            self.text = text
            self.widget.bind("<Enter>", self.enter)
            self.widget.bind("<Leave>", self.close)
        def enter(self, event=None):
            x = y = 0
            x, y, cx, cy = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 20
            # creates a toplevel window
            self.tw = tk.Toplevel(self.widget)
            # Leaves only the label and removes the app window
            self.tw.wm_overrideredirect(True)
            self.tw.wm_geometry("+%d+%d" % (x, y))
            label = tk.Label(self.tw, text=self.text, justify='left',
                        bg=config['colors']['bgcolor'], fg=config['colors']['textcolor'], relief='solid', borderwidth=1,
                        font=("times", "12", "normal"))
            label.pack(ipadx=1)
        def close(self, event=None):
            if self.tw:
                self.tw.destroy()
    global parameters
    global name
    item = e.get()

    parameters = {
        "query": {
            "status": {
                "option": "online"
            },
            "name": item,
            "stats": [{
                "type": "and",
                "filters": []
            }]
        },
        "sort": {
            "price": "asc"
        }
    }

    name = parameters['query']['name']
    response = requests.post("https://www.pathofexile.com/api/trade/search/Standard", json=parameters)

    try:

        query = response.json()["id"]
        result = response.json()["result"][:10]
        result = json.dumps(result)
        result = result.replace('[', '')
        result = result.replace(']', '')
        result = result.replace('"', '')
        result = result.replace(' ', '')

        response = requests.get("https://www.pathofexile.com/api/trade/fetch/{}?query={}".format(result, query))
        result = response.json()["result"]
        buy_frame = Tk()
        buy_frame.configure(background=config['colors']['bgcolor'])
        buy_frame.geometry('400x300+200+200')
        buy_frame.title(name)

        r = 0
        wr = {}
        for d in result:
            if d['listing']['price'] is not None:
                amount = d['listing']['price']['amount']
                currency = d['listing']['price']['currency']
                nick = d['listing']['account']['lastCharacterName']
                whisper = d['listing']['whisper']
                mods = "\n".join(d['item']['explicitMods'])
                
                if 'corrupted' in d['item']:
                    wr[r] = tk.Label(buy_frame, text="price {} {} Corrupt - {}".format(amount, currency, nick),
                                     fg=config['colors']['textcolor'], bg=config['colors']['bgcolor'])
                    wr[r].grid(row=r)
                    tk.Button(buy_frame, text="Buy", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'],
                                      command=lambda whisper=whisper: buyitem(whisper)).grid(row=r, column=1)
                    CreateToolTip(wr[r], mods)


                else:
                    wr[r] = tk.Label(buy_frame, text="price {} {} - {}".format(amount, currency, nick), fg=config['colors']['textcolor'],
                                     bg=config['colors']['bgcolor'])
                    wr[r].grid(row=r)
                    tk.Button(buy_frame, text="Buy", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'],
                                      command=lambda whisper=whisper: buyitem(whisper)).grid(row=r, column=1)
                    CreateToolTip(wr[r], mods)


                r = r + 1
        tk.Button(buy_frame, text="Show on web", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'],
                         command=lambda: webbrowser.open(
                             "https://www.pathofexile.com/trade/search/Standard/" + query)).grid(row=r, column=0)
        buy_frame.call('wm', 'attributes', '.', '-topmost', '1')
        buy_frame.mainloop()
    except:
        MessFrame = Tk()
        MessFrame.configure(background=config['colors']['bgcolor'])
        MessFrame.geometry('150x50+200+200')
        MessFrame.title("Pricecheck")
        tk.Label(MessFrame, text="No result's Found", fg=config['colors']['textcolor'], bg=config['colors']['bgcolor']).grid(row=0, column=0, columnspan=2)
        MessFrame.call('wm', 'attributes', '.', '-topmost', '1')
        MessFrame.mainloop()
        
def searchgemwindow():
    global parameters
    global name
    item = g.get()
    lvl = l.get()
    qual = q.get()
    corr = var.get()

    if corr is True:
        corr = "true"
    else:
        corr = "false"

    parameters = {
        "query": {
            "status": {
                "option": "online"
            },
            "type": item,
            "stats": [{
                "type": "and",
                "filters": []
            }],
            "filters": {
                "misc_filters": {
                    "filters": {
                        "gem_level": {
                            "min": lvl,
                            "max": lvl
                        },
                        "quality": {
                            "min": qual,
                            "max": qual,
                        }
                        ,
                        "corrupted": {
                            "option": corr
                        }
                    }
                }
            }
        },
        "sort": {
            "price": "asc"
        }
    }

    name = parameters['query']['type']
    response = requests.post("https://www.pathofexile.com/api/trade/search/Standard", json=parameters)

    try:

        query = response.json()["id"]
        result = response.json()["result"][:10]
        result = json.dumps(result)
        result = result.replace('[', '')
        result = result.replace(']', '')
        result = result.replace('"', '')
        result = result.replace(' ', '')

        response = requests.get("https://www.pathofexile.com/api/trade/fetch/{}?query={}".format(result, query))
        result = response.json()["result"]
        buy_frame = Tk()
        buy_frame.configure(background=config['colors']['bgcolor'])
        buy_frame.title(name)

        r = 0
        wr = {}
        for d in result:
            lvl = 0
            qual = 0
            if d['listing']['price'] is not None:
                amount = d['listing']['price']['amount']
                currency = d['listing']['price']['currency']
                nick = d['listing']['account']['lastCharacterName']
                whisper = d['listing']['whisper']
                
                if 'corrupted' in d['item']:
                    
                    wr[r] = tk.Label(buy_frame, text="price {} {} Corrupt - {}".format(amount, currency, nick),
                                     fg=config['colors']['textcolor'], bg=config['colors']['bgcolor'])
                    wr[r].grid(row=r)
                    tk.Button(buy_frame, text="Buy", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'],
                                      command=lambda whisper=whisper: buyitem(whisper)).grid(row=r, column=1)
                

                else:
                    wr[r] = tk.Label(buy_frame, text="price {} {} - {}".format(amount, currency, nick), fg=config['colors']['textcolor'],
                                     bg=config['colors']['bgcolor'])
                    wr[r].grid(row=r)
                    tk.Button(buy_frame, text="Buy", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'],
                                      command=lambda whisper=whisper: buyitem(whisper)).grid(row=r, column=1)
           

                r = r + 1
        tk.Button(buy_frame, text="Show on web", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'],
                         command=lambda: webbrowser.open(
                             "https://www.pathofexile.com/trade/search/Standard/" + query)).grid(row=r, column=0)
        buy_frame.call('wm', 'attributes', '.', '-topmost', '1')
        buy_frame.mainloop()
    except:
        MessFrame = Tk()
        MessFrame.configure(background=config['colors']['bgcolor'])
        MessFrame.geometry('150x50+200+200')
        MessFrame.title("Pricecheck")
        tk.Label(MessFrame, text="No result's Found", fg=config['colors']['textcolor'], bg=config['colors']['bgcolor']).grid(row=0, column=0, columnspan=2)
        MessFrame.call('wm', 'attributes', '.', '-topmost', '1')
        MessFrame.mainloop()

def searchotherset():
    global parameters
    global name
    item = o.get()

    parameters = {
        "query": {
            "status": {
                "option": "online"
            },
            "term": item,
            "stats": [{
                "type": "and",
                "filters": []
            }]
        },
        "sort": {
            "price": "asc"
        }
    }

    name = parameters['query']['term']
    response = requests.post("https://www.pathofexile.com/api/trade/search/Standard", json=parameters)

    try:

        query = response.json()["id"]
        result = response.json()["result"][:10]
        result = json.dumps(result)
        result = result.replace('[', '')
        result = result.replace(']', '')
        result = result.replace('"', '')
        result = result.replace(' ', '')

        response = requests.get("https://www.pathofexile.com/api/trade/fetch/{}?query={}".format(result, query))
        result = response.json()["result"]
        buy_frame = Tk()
        buy_frame.configure(background=config['colors']['bgcolor'])
        buy_frame.geometry('400x300+200+200')
        buy_frame.title(name)

        r = 0
        wr = {}
        for d in result:
            if d['listing']['price'] is not None:
                amount = d['listing']['price']['amount']
                currency = d['listing']['price']['currency']
                nick = d['listing']['account']['lastCharacterName']
                whisper = d['listing']['whisper']

                
                if 'corrupted' in d['item']:
                    wr[r] = tk.Label(buy_frame, text="price {} {} Corrupt - {}".format(amount, currency, nick),
                                     fg=config['colors']['textcolor'], bg=config['colors']['bgcolor'])
                    wr[r].grid(row=r)
                    tk.Button(buy_frame, text="Buy", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'],
                                      command=lambda whisper=whisper: buyitem(whisper)).grid(row=r, column=1)


                else:
                    wr[r] = tk.Label(buy_frame, text="price {} {} - {}".format(amount, currency, nick), fg=config['colors']['textcolor'],
                                     bg=config['colors']['bgcolor'])
                    wr[r].grid(row=r)
                    tk.Button(buy_frame, text="Buy", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'],
                                      command=lambda whisper=whisper: buyitem(whisper)).grid(row=r, column=1)


                r = r + 1
        tk.Button(buy_frame, text="Show on web", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'],
                         command=lambda: webbrowser.open(
                             "https://www.pathofexile.com/trade/search/Standard/" + query)).grid(row=r, column=0)
        buy_frame.call('wm', 'attributes', '.', '-topmost', '1')
        buy_frame.mainloop()
    except:
        MessFrame = Tk()
        MessFrame.configure(background=config['colors']['bgcolor'])
        MessFrame.geometry('150x50+200+200')
        MessFrame.title("Pricecheck")
        tk.Label(MessFrame, text="No result's Found", fg=config['colors']['textcolor'], bg=config['colors']['bgcolor']).grid(row=0, column=0, columnspan=2)
        MessFrame.call('wm', 'attributes', '.', '-topmost', '1')
        MessFrame.mainloop()

def setclienttxt():
    clientwindow = tk.Tk()
    clientwindow.filename = filedialog.askopenfilename(initialdir="/", title="Please choose your Client.txt",
                                                        filetypes=(("Text", "*.txt"), ("all files", "*.*")))
    
    config['FILES']['clienttxt'] = clientwindow.filename
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    clientwindow.destroy()

    clientwindow.mainloop()


def setsound():
    soundwindow = tk.Tk()
    soundwindow.filename = filedialog.askopenfilename(initialdir="/", title="Select file", filetypes=(
        ("Wave", "*.wav"), ("Mp3", "*.mp3"), ("all files", "*.*")))
    config['FILES']['soundfile'] = soundwindow.filename
    if sys.platform == "linux":
        filetosave = '{}/config.ini'.format(os.getcwd())
    else:
        filetosave = '{}\config.ini'.format(os.getcwd())
    with open(filetosave, 'w') as configfile:
        config.write(configfile)
    soundwindow.destroy()

    soundwindow.mainloop()


def setty(tytext):
    config['FILES']['tytrade'] = tytext
    if sys.platform == "linux":
        filetosave = '{}/config.ini'.format(os.getcwd())
    else:
        filetosave = '{}\config.ini'.format(os.getcwd())
    with open(filetosave, 'w') as configfile:
        config.write(configfile)


def startopt():
    optray = threading.Thread(target=creatoptions)
    optray.start()


def stcolor(which, entry):
    (triple, hexstr) = askcolor()
    config['colors'][which] = hexstr
    if sys.platform == "linux":
        filetosave = '{}/config.ini'.format(os.getcwd())
    else:
        filetosave = '{}\config.ini'.format(os.getcwd())
    with open(filetosave, 'w') as configfile:
        config.write(configfile)

    entry.delete(0, 100)
    entry.insert(0, hexstr)


def resetcount(awakener, act):
    config['awakener'][awakener] = str(0)
    if sys.platform == "linux":
        filetosave = '{}/config.ini'.format(os.getcwd())
    else:
        filetosave = '{}\config.ini'.format(os.getcwd())
    with open(filetosave, 'w') as configfile:
        config.write(configfile)
   
    act.config(text=config['awakener'][awakener])

def startbuy():
    buytray = threading.Thread(target=createbuymenu)
    buytray.start()
    
def createbuymenu():
    global e
    global g
    global l
    global q
    global c
    global o
    global var
    
    
    buywindow = tk.Tk()
    buywindow.title("Buy")
    buywindow.configure(background=config['colors']['bgcolor'])
    
    tk.Label(buywindow, text="Unique Item Search", fg=config['colors']['textcolor'], bg=config['colors']['bgcolor']).grid(row=1, column=1)
    e = tk.Entry(buywindow, width=30, fg=config['colors']['fgcolor'], bg=config['colors']['bgcolor'])
    e.grid(row=1, column=2)
    tk.Button(buywindow, text="Search", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'], command=searchwindowset).grid(
        row=1, column=6)
    
    tk.Label(buywindow, text="Gem Search", fg=config['colors']['textcolor'], bg=config['colors']['bgcolor']).grid(row=2, column=1)
    g = tk.Entry(buywindow, width=30, fg=config['colors']['fgcolor'], bg=config['colors']['bgcolor'])
    g.grid(row=2, column=2)
    l = tk.Entry(buywindow, width=3, fg=config['colors']['fgcolor'], bg=config['colors']['bgcolor'])
    l.insert(END, 'LVL')
    l.grid(row=2, column=3)
    q = tk.Entry(buywindow, width=3, fg=config['colors']['fgcolor'], bg=config['colors']['bgcolor'])
    q.insert(END, '%')
    q.grid(row=2, column=4)
    var = tk.BooleanVar(buywindow, True)
    c = tk.Checkbutton(buywindow, text="Corrupted", offvalue=0, onvalue=1, variable=var, fg=config['colors']['fgcolor'], bg=config['colors']['bgcolor'])
    c.grid(row=2, column=5)
    tk.Button(buywindow, text="Search", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'], command=searchgemwindow).grid(
        row=2, column=6)
    
    tk.Label(buywindow, text="Currency / Prophecy / Card Search", fg=config['colors']['textcolor'], bg=config['colors']['bgcolor']).grid(row=3, column=1)
    o = tk.Entry(buywindow, width=30, fg=config['colors']['fgcolor'], bg=config['colors']['bgcolor'])
    o.grid(row=3, column=2)
    tk.Button(buywindow, text="Search", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'], command=searchotherset).grid(
        row=3, column=6)
    
    buywindow.call('wm', 'attributes', '.', '-topmost', '1')
    buywindow.mainloop()


    
def createmainmenu():
    global act1
    global act2
    global act3
    global act4
   
    menuwindow = tk.Tk()
    menuwindow.title("Poe Tools")
    menuwindow.configure(background=config['colors']['bgcolor'])
    tk.Label(menuwindow, text="Welcome to Poe Tools", fg=config['colors']['textcolor'], bg=config['colors']['bgcolor']).grid(row=0, column=2)
    

    tk.Label(menuwindow, text="Redeemer: ", fg=config['colors']['textcolor'], bg=config['colors']['bgcolor']).grid(row=2, column=1)
    act1 = tk.Label(menuwindow, text=config['awakener']['redeemer'], fg=config['colors']['textcolor'], bg=config['colors']['bgcolor'])
    act1.grid(row=2, column=2)
    tk.Button(menuwindow, text="reset", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'],
                     command=lambda: resetcount("redeemer", act1)).grid(row=2, column=3)

    tk.Label(menuwindow, text="Crusader: ", fg=config['colors']['textcolor'], bg=config['colors']['bgcolor']).grid(row=3, column=1)
    act2 = tk.Label(menuwindow, text=config['awakener']['crusader'], fg=config['colors']['textcolor'], bg=config['colors']['bgcolor'])
    act2.grid(row=3, column=2)
    tk.Button(menuwindow, text="reset", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'],
                     command=lambda: resetcount("crusader", act2)).grid(row=3, column=3)

    tk.Label(menuwindow, text="Warlord: ", fg=config['colors']['textcolor'], bg=config['colors']['bgcolor']).grid(row=4, column=1)
    act3 = tk.Label(menuwindow, text=config['awakener']['warlord'], fg=config['colors']['textcolor'], bg=config['colors']['bgcolor'])
    act3.grid(row=4, column=2)
    tk.Button(menuwindow, text="reset", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'],
                     command=lambda: resetcount("warlord", act3)).grid(row=4, column=3)

    tk.Label(menuwindow, text="Hunter: ", fg=config['colors']['textcolor'], bg=config['colors']['bgcolor']).grid(row=5, column=1)
    act4 = tk.Label(menuwindow, text=config['awakener']['hunter'], fg=config['colors']['textcolor'], bg=config['colors']['bgcolor'])
    act4.grid(row=5, column=2)
    tk.Button(menuwindow, text="reset", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'],
                     command=lambda: resetcount("hunter", act4)).grid(row=5, column=3)

    tk.Button(menuwindow, text="Options", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'], command=startopt).grid(row=6,
                                                                                                               column=1)
    tk.Button(menuwindow, text="Buy", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'], command=startbuy).grid(row=6,
                                                                                                               column=2)

    menuwindow.call('wm', 'attributes', '.', '-topmost', '1')
    menuwindow.mainloop()

def createmainmenuthread():
    smtray = threading.Thread(target=createmainmenu)
    smtray.start()

def creatoptions():
    optionwindow = tk.Tk()
    optionwindow.title("Options")
    optionwindow.configure(background=config['colors']['bgcolor'])
    optionwindow.geometry('600x300+200+200')
    tk.Label(optionwindow, text="Client.txt", fg=config['colors']['textcolor'], bg=config['colors']['bgcolor']).grid(row=2, column=1)
    f = tk.Entry(optionwindow, width=30, fg=config['colors']['fgcolor'], bg=config['colors']['bgcolor'])
    f.insert(0, config['FILES']['clienttxt'])
    f.grid(row=2, column=2)
    btn2 = tk.Button(optionwindow, text="Set", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'], command=setclienttxt)
    btn2.grid(row=2, column=3)

    tk.Label(optionwindow, text="Trade Sound", fg=config['colors']['textcolor'], bg=config['colors']['bgcolor']).grid(row=3, column=1)
    g = tk.Entry(optionwindow, width=30, fg=config['colors']['fgcolor'], bg=config['colors']['bgcolor'])
    g.insert(0, config['FILES']['soundfile'])
    g.grid(row=3, column=2)
    btn3 = tk.Button(optionwindow, text="Set", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'], command=setsound)
    btn3.grid(row=3, column=3)

    tk.Label(optionwindow, text="Ty Text", fg=config['colors']['textcolor'], bg=config['colors']['bgcolor']).grid(row=4, column=1)
    g = tk.Entry(optionwindow, width=30, fg=config['colors']['fgcolor'], bg=config['colors']['bgcolor'])
    g.insert(0, config['FILES']['tytrade'])
    g.grid(row=4, column=2)
    btn4 = tk.Button(optionwindow, text="Set", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'], command=lambda: setty(g.get()))
    btn4.grid(row=4, column=3)

    tk.Label(optionwindow, text="Button Foreground Color", fg=config['colors']['textcolor'], bg=config['colors']['bgcolor']).grid(row=5,
                                                                                                            column=1)
    g4 = tk.Entry(optionwindow, width=30, fg=config['colors']['fgcolor'], bg=config['colors']['bgcolor'])
    g4.insert(0, config['colors']['fgcolor'])
    g4.grid(row=5, column=2)
    btn5 = tk.Button(optionwindow, text="Set", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'],
                     command=lambda: stcolor("fgcolor", g4))
    btn5.grid(row=5, column=3)

    tk.Label(optionwindow, text="Button Background Color", fg=config['colors']['textcolor'], bg=config['colors']['bgcolor']).grid(row=6,
                                                                                                            column=1)
    g5 = tk.Entry(optionwindow, width=30, fg=config['colors']['fgcolor'], bg=config['colors']['bgcolor'])
    g5.insert(0, config['colors']['bgcolor'])
    g5.grid(row=6, column=2)
    btn5 = tk.Button(optionwindow, text="Set", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'],
                     command=lambda: stcolor("bgcolor", g5))
    btn5.grid(row=6, column=3)

    tk.Label(optionwindow, text="Text Color", fg=config['colors']['textcolor'], bg=config['colors']['bgcolor']).grid(row=7, column=1)
    g6 = tk.Entry(optionwindow, width=30, fg=config['colors']['fgcolor'], bg=config['colors']['bgcolor'])
    g6.insert(0, config['colors']['textcolor'])
    g6.grid(row=7, column=2)
    btn6 = tk.Button(optionwindow, text="Set", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'],
                     command=lambda: stcolor("textcolor", g6))
    btn6.grid(row=7, column=3)

    optionwindow.call('wm', 'attributes', '.', '-topmost', '1')
    optionwindow.mainloop()
