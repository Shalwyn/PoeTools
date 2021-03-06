#!/usr/bin/python
# -*- coding: utf-8 -*-#

import functions.pricecheck as pricecheck
from functions.keyfunctions import watch_keyboard
import sys
import os
import functions.config as config
import functions.tradeget as tradeget
import threading
import time
import tkinter as tk
from tkinter import filedialog
import psutil
import PySimpleGUIQt as sg
import configparser
import functions.menu as menu

menu_def = ['File', ['Options', '&Buy', '---', 'E&xit']]

menu.createmainmenuthread()

keyth = threading.Thread(target=watch_keyboard)
keyth.start()

prev = ""
prevst = ""
root = tk.Tk()
root.update()
root.withdraw()
DEBUG = False
i = 0
global lastlinesold
global lastlinesnew

config = configparser.ConfigParser()
if sys.platform == "linux":
    config.read('{}/config.ini'.format(os.getcwd()))
else:
    config.read('{}\config.ini'.format(os.getcwd()))



def checkclienttxt():
    try:
        open(config['FILES']['clienttxt'] , "r")
    except IOError:
        clientwindow = tk.Tk()
        clientwindow.filename = filedialog.askopenfilename(initialdir="/", title="Please choose your Client.txt",
                                                           filetypes=(("Text", "*.txt"), ("all files", "*.*")))
        print(clientwindow.filename)
        config['FILES']['clienttxt'] = clientwindow.filename
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        clientwindow.destroy()

        clientwindow.mainloop()


checkclienttxt()

originalTime = os.path.getmtime(config['FILES']['clienttxt'])

def traymake():
    
    tray = sg.SystemTray(menu=menu_def, filename=r'icon.png')
    while True:
        menu_item = tray.Read()
        if menu_item == 'Exit':
            if sys.platform == "linux":
                PROCNAME = "python3"
                for proc in psutil.process_iter():
                    # check whether the process name matches
                    if proc.name() == PROCNAME:
                        proc.kill()
            else:
                PROCNAME = "poetools.exe"

                for proc in psutil.process_iter():
                    # check whether the process name matches
                    if proc.name() == PROCNAME:
                        proc.kill()
        if menu_item == "Options":
            menu.startopt()
        if menu_item == "Buy":
            menu.startbuy()

trayth = threading.Thread(target=traymake)
trayth.start()

lastlinesold = sum(1 for line in open(config['FILES']['clienttxt'], 'r', encoding='UTF8'))
lastseenline = ""

while True:

    try:
        data = root.clipboard_get()
    except (tk.TclError, UnicodeDecodeError) as e:  # ignore non-text clipboard contents
        print(e)
        continue

    splitdata = data.splitlines()
    if "Rarity: Unique" in data and config['FILES'].getint('statsearch') == 0:
        if data != prev:
            prev = data
            pricecheck.buildunique(data)
            t80 = threading.Thread(target=pricecheck.buildpricewindow)
            t80.start()

    elif "Rarity: Unique" in data and config['FILES'].getint('statsearch') == 1:

        if data != prevst:
            prevst = data
            prev = data
            pricecheck.builduniquestat(data)
            t81 = threading.Thread(target=pricecheck.buildpricewindow)
            t81.start()
            config = configparser.ConfigParser()
            if sys.platform == "linux":
                config.read('{}/config.ini'.format(os.getcwd()))
            else:
                config.read('{}\config.ini'.format(os.getcwd()))
            config['FILES']['statsearch'] = str(0)
            with open('config.ini', 'w') as configfile:
                config.write(configfile)

    elif "Map Tier:" in data and ("Rarity: Rare" in data or "Rarity: Normal" in data or "Rarity: Magic" in data):
        if data != prev:
            prev = data
            pricecheck.buildmap(data)
            t82 = threading.Thread(target=pricecheck.buildpricewindow)
            t82.start()

    elif "Rarity: Currency" in data:
        if data != prev:
            prev = data
            pricecheck.buildcurrency(data)
            t83 = threading.Thread(target=pricecheck.buildpricewindowcurrency)
            t83.start()
            
    elif "Rarity: Divination Card" in data:
        if data != prev:
            prev = data
            pricecheck.buildrest(data)
            t83 = threading.Thread(target=pricecheck.buildpricewindow)
            t83.start()
            
    elif "Rarity: Gem" in data:

        if data != prev:
            prev = data
            pricecheck.buildgem(data)
            t84 = threading.Thread(target=pricecheck.buildpricewindow)
            t84.start()

    elif "Rarity: Rare" in data and splitdata[3] == "--------":
        if data != prev:
            prev = data
            pricecheck.buildrareitem(data)
            t85 = threading.Thread(target=pricecheck.buildpricewindow)
            t85.start()

    elif "Rarity: Normal" in data:
        if data != prev:
            prev = data
            pricecheck.buildnormal(data)
            t84 = threading.Thread(target=pricecheck.buildpricewindow)
            t84.start()

    if os.path.getmtime(config['FILES']['clienttxt']) > originalTime:
        
        config = configparser.ConfigParser()
        if sys.platform == "linux":
            config.read('{}/config.ini'.format(os.getcwd()))
        else:
            config.read('{}\config.ini'.format(os.getcwd()))
        ding = open(config['FILES']['clienttxt'], 'r', encoding='UTF8')
        lastlinesnew = sum(1 for line in ding)

        while lastlinesold < lastlinesnew:
            last_line = open(config['FILES']['clienttxt'], 'r', encoding='UTF8').readlines()[lastlinesold]

            if tradeget.league in last_line and "@From" in last_line:
                try:
                    if tradeget.window.winfo_exists() is not None:
                        tradeget.addtabtrade(tradeget.window, tradeget.tasktabs, last_line)
                except:
                    tradeget.tradewindowthreat(last_line)
                   


            if tradeget.league in last_line and "@To" in last_line:
                t18 = threading.Thread(target=tradeget.outgoinwindow)
                t18.start()

            if "Redeemer" in last_line and config['awakener'].getint('redeemer') < 3 and "Redeember" not in lastseenline:
                newwrite = config['awakener'].getint('redeemer') + 1
                config.set('awakener', 'redeemer', str(newwrite))
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)
                menu.act1.config(text=config['awakener'].getint('redeemer'))


            if "Crusader" in last_line and config['awakener'].getint('crusader') < 3 and "Crusader" not in lastseenline:
                newwrite = config['awakener'].getint('crusader') + 1
                config.set('awakener', 'crusader', str(newwrite))
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)
                menu.act2.config(text=config['awakener'].getint('crusader'))

            if "Warlord" in last_line and config['awakener'].getint('warlord') < 3 and "Warlord" not in lastseenline:
                newwrite = config['awakener'].getint('warlord') + 1
                config.set('awakener', 'warlord', str(newwrite))
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)
                menu.act3.config(text=config['awakener'].getint('warlord'))

            if "Hunter" in last_line and config['awakener'].getint('hunter') < 3 and "Hunter" not in lastseenline:
                newwrite = config['awakener'].getint('hunter') + 1
                config.set('awakener', 'hunter', str(newwrite))
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)
                menu.act4.config(text=config['awakener'].getint('hunter'))
                # menu.act1.configure(text=config.redeemer)
            lastlinesold = lastlinesold + 1
            lastseenline = last_line
        ding.close()
        originalTime = os.path.getmtime(config['FILES']['clienttxt'])
