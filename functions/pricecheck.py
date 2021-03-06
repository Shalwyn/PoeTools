
import json
import requests
import re
import tkinter as tk
from tkinter import filedialog

import functions.modlist as modlist
import functions.config as config
import webbrowser
import configparser
import os
import sys
import functions.currency as currency

config = configparser.ConfigParser()
if sys.platform == "linux":
    config.read('{}/config.ini'.format(os.getcwd()))
else:
    config.read('{}\config.ini'.format(os.getcwd()))
global MessFrame

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

def checkifcurrepted(itemparse):
    if "Corrupted" in itemparse:
        return "true"
    else:
        return "false"

def buildrest(itemparse):
    global parameters
    global name
    parameters = {
        "query": {
            "status": {
                "option": "online"
            },
            "type": itemparse.splitlines()[1],
            "stats": [{
                "type": "and",
                "filters": []
            }]
        },
        "sort": {
            "price": "asc"
        }
    }
    name = parameters['query']['type']

def buildunique(itemparse):
    global parameters
    global name
    parameters = {
        "query": {
            "status": {
                "option": "online"
            },
            "name": itemparse.splitlines()[1],
            "type": itemparse.splitlines()[2],
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

def builduniquestat(itemparse):
    links = 0
    global parameters
    global name
    splitmap = itemparse.splitlines()
    mod = {}
    value = {}
    implicits = {}
    valueimp = {}
    k = 0
    for x in range(0, itemparse.count('\n')):
        if "Item Level:" in splitmap[x]:
            beginstat = x
            if splitmap[x-2].count('-') != 0:
                links = splitmap[x-2].count('-') + 1
            if "Allocates" in splitmap[beginstat+2]:
                beginstat = beginstat+2
            if "(implicit)" in splitmap[beginstat+2]:

                for y in range(beginstat+2, beginstat+10):
                    if "(implicit)" in splitmap[y]:
                        implicits[k] = splitmap[y]
                        k = k + 1

                beginstat = beginstat+4
                break
            else:
                beginstat = x+2


    for x in range(beginstat, itemparse.count('\n')):
        if splitmap[x] == "--------":
            endstep = x
            break

    parameters = {
        "query": {
            "status": {
                "option": "online"
            },
            "name": itemparse.splitlines()[1],
            "type": itemparse.splitlines()[2],
            "filters": {
                "socket_filters": {
                    "filters": {
                        "links": {
                            "min": links
                        }
                    }
                }
            }
        },
        "sort": {
            "price": "asc"
        },

    }


    name = "StatCheck: {} - {} Linked".format(parameters['query']['name'], links)
    parameters["query"]["stats"] = [{}]
    parameters["query"]["stats"][0]["type"] = "and"
    parameters["query"]["stats"][0]["filters"] = []

    z = 0

    for x in range (0, len(implicits)):
        valueimp[x] = implicits[x].replace('+', '')
        valueimp[x] = re.sub(r"[^0-9-.]", "", valueimp[x])

        implicits[x] = implicits[x].replace('+', '')
        implicits[x] = re.sub("[^a-zA-Z %]+", "#", implicits[x])
        implicits[x] = implicits[x][:-10]

        if "#% reduced Mana Reserved" in implicits[x]:
            implicits[x] = "#% increased Mana Reserved"
            valueimp[x] = int(valueimp[x]) * -1
            valueimp[x] = str(valueimp[x])

        if implicits[x] in modlist.mods:

            for y in range(0, len(modlist.mods[implicits[x]])):
                if "implicit" in modlist.mods[implicits[z]][y]:
                    implicitstat = modlist.mods[implicits[z]][y]
            min = valueimp[x]

            parameters["query"]["stats"][0]["filters"].append({"id": implicitstat, "value": {"min": min}})

    jprint(parameters)

    for y in range(beginstat, endstep):



        mod[z] = splitmap[y].replace('+', '')
        mod[z] = re.sub("[^a-zA-Z %]+", "#", mod[z])
        #mod[z] = re.sub(r"\d+", "#", mod[z])


        if mod[z] == "#% increased Armour and Energy Shield":
            if "augmented" in itemparse:
                mod[z] = "#% increased Armour and Energy Shield (Local)"
        elif mod[z] == "#% increased Armour and Evasion":
            if "augmented" in itemparse:
                mod[z] = "#% increased Armour and Evasion (Local)"
        elif mod[z] == "#% increased Armour, Evasion and Energy Shield":
            if "augmented" in itemparse:
                mod[z] = "#% increased Armour, Evasion and Energy Shield (Local)"
        elif mod[z] == "#% increased Energy Shield":
            if "augmented" in itemparse:
                mod[z] = "#% increased Energy Shield (Local)"
        elif mod[z] == "#% increased Evasion and Energy Shield":
            if "augmented" in itemparse:
                mod[z] = "#% increased Evasion and Energy Shield (Local)"
        elif mod[z] == "#% increased Armour":
            if "augmented" in itemparse:
                mod[z] = "#% increased Armour (Local)"
        elif mod[z] == "# to Armour":
            if "augmented" in itemparse:
                mod[z] = "# to Armour (Local)"
        elif mod[z] == "# to maximum Energy Shield":
            if "augmented" in itemparse:
                mod[z] = "# to maximum Energy Shield (Local)"
        elif mod[z] == "#% increased Evasion Rating":
            if "augmented" in itemparse:
                mod[z] = "#% increased Evasion Rating (Local)"



        value[z] = splitmap[y].replace('+', '')
        value[z] = re.sub(r"[^0-9-]", "", value[z])

        if "Adds" in splitmap[y] and ("Physical Damage" in splitmap[y] or "Chaos Damage" in splitmap[y] or "Cold Damage" in splitmap[y] or "Fire Damage" in splitmap[y] or "Lightning Damage" in splitmap[y]) and "to" in splitmap[y]:
            mintomod = splitmap[y].split()
            value[z] = (int(mintomod[1]) + int(mintomod[3])) / 2


        if mod[z] in modlist.mods:

            for x in range(0, len(modlist.mods[mod[z]])):
                if "explicit" in modlist.mods[mod[z]][x]:
                    explicitstat = modlist.mods[mod[z]][x]
            min = value[z]
            parameters["query"]["stats"][0]["filters"].append({"id": explicitstat, "value": {"min": min}})
        #addfiltermods["filters"].update(addmod)
        z = z + 1

    #jprint(parameters)
    #addfilter["stats"].update(addfiltermods)
    #parameters["query"].update(addfilter)


def buildrareitem(itemparse):
    links = 0
    global parameters
    global name
    global mod
    global value
    value = {}
    mod = {}
    endstep = itemparse.count('\n')
    splitmap = itemparse.splitlines()
    implicits = {}
    valueimp = {}
    k = 0
    for x in range(0, itemparse.count('\n')):

        if "Item Level:" in splitmap[x]:
            beginstat = x
            if splitmap[x-2].count('-') != 0:
                links = splitmap[x-2].count('-') + 1
            if "Allocates" in splitmap[beginstat+2]:
                beginstat = beginstat+2

            if "(implicit)" in splitmap[beginstat+2]:

                for y in range(beginstat+2, beginstat+5):
                    if "(implicit)" in splitmap[y]:
                        implicits[k] = splitmap[y]
                        k = k + 1

                beginstat = beginstat+4
                break
            
            else:
                beginstat = x+2
                
    if splitmap[beginstat+1] == "--------":
        beginstat = beginstat + 2
                


    for x in range(beginstat, itemparse.count('\n')):
        if splitmap[x] == "--------":
            endstep = x
            break


    if links < 4:
        links = None

    parameters = {
        "query": {
            "status": {
                "option": "online"
            },
            "type": itemparse.splitlines()[2],

            "filters": {
                "socket_filters": {
                    "filters": {
                        "links": {
                            "min": links
                        }
                    }
                }
            }
        },
        "sort": {
            "price": "asc"
        },

    }


    name = "StatCheck: {} - {} Linked".format(parameters['query']['type'], links)
    parameters["query"]["stats"] = [{}]
    parameters["query"]["stats"][0]["type"] = "and"
    parameters["query"]["stats"][0]["filters"] = []

    z = 0

    for x in range (0, len(implicits)):
        valueimp[x] = implicits[x].replace('+', '')
        valueimp[x] = re.sub(r"[^0-9-.]", "", valueimp[x])

        implicits[x] = implicits[x].replace('+', '')
        implicits[x] = re.sub("[^a-zA-Z %]+", "#", implicits[x])
        implicits[x] = implicits[x][:-11]

        if "#% reduced Mana Reserved" in implicits[x]:
            implicits[x] = "#% increased Mana Reserved"
            valueimp[x] = int(valueimp[x]) * -1
            valueimp[x] = str(valueimp[x])

        if "Staff" in itemparse:
            if "Chance to Block Attack Damage while wielding a Staff" in implicits[x]:
                implicits[x] = "#% Chance to Block Attack Damage while wielding a Staff (Staves)"
            

        if implicits[x] in modlist.mods:

            for y in range(0, len(modlist.mods[implicits[x]])):
                if "implicit" in modlist.mods[implicits[z]][y]:
                    implicitstat = modlist.mods[implicits[z]][y]
            min = valueimp[x]

            parameters["query"]["stats"][0]["filters"].append({"id": implicitstat, "value": {"min": min}})


    for y in range(beginstat, endstep):
        mod[z] = splitmap[y].replace('+', '')
        mod[z] = re.sub("[^a-zA-Z %]+", "#", mod[z])
        #mod[z] = re.sub(r"\d+", "#", mod[z])


        if mod[z] == "#% increased Armour and Energy Shield":
            if "augmented" in itemparse:
                mod[z] = "#% increased Armour and Energy Shield (Local)"
        elif mod[z] == "#% increased Armour and Evasion":
            if "augmented" in itemparse:
                mod[z] = "#% increased Armour and Evasion (Local)"
        elif mod[z] == "#% increased Armour, Evasion and Energy Shield":
            if "augmented" in itemparse:
                mod[z] = "#% increased Armour, Evasion and Energy Shield (Local)"
        elif mod[z] == "#% increased Energy Shield":
            if "augmented" in itemparse:
                mod[z] = "#% increased Energy Shield (Local)"
        elif mod[z] == "#% increased Evasion and Energy Shield":
            if "augmented" in itemparse:
                mod[z] = "#% increased Evasion and Energy Shield (Local)"
        elif mod[z] == "#% increased Armour":
            if "augmented" in itemparse:
                mod[z] = "#% increased Armour (Local)"
        elif mod[z] == "# to Armour":
            if "augmented" in itemparse:
                mod[z] = "# to Armour (Local)"
        elif mod[z] == "# to maximum Energy Shield":
            if "augmented" in itemparse:
                mod[z] = "# to maximum Energy Shield (Local)"
        elif mod[z] == "#% increased Attack Speed":
            if "augmented" in itemparse:
                mod[z] = "#% increased Attack Speed (Local)"
        elif mod[z] == "#% increased Evasion Rating":
            if "augmented" in itemparse:
                mod[z] = "#% increased Evasion Rating (Local)"
        elif mod[z] == "# to Evasion Rating":
            if "augmented" in itemparse:
                mod[z] = "# to Evasion Rating (Local)"



        value[z] = splitmap[y].replace('+', '')
        value[z] = re.sub(r"[^0-9-.]", "", value[z])

        if "Adds" in splitmap[y]:
            if "Physical Damage" in splitmap[y] or "Chaos Damage" in splitmap[y] or "Cold Damage" in splitmap[y] or "Fire Damage" in splitmap[y] or "Lightning Damage" in splitmap[y] and "to" in splitmap[y]:
                mintomod = splitmap[y].split()
                value[z] = (int(mintomod[1]) + int(mintomod[3])) / 2

        if "Minions deal" in splitmap[y]:
            if "Physical Damage" in splitmap[y] or "Chaos Damage" in splitmap[y] or "Cold Damage" in splitmap[y] or "Fire Damage" in splitmap[y] or "Lightning Damage" in splitmap[y] and "to" in splitmap[y]:
                mintomod = splitmap[y].split()
                value[z] = (int(mintomod[2]) + int(mintomod[4])) / 2

        if "crafted" in mod[z]:
            mod[z] = mod[z][:-10]
            if mod[z] in modlist.mods:

                for x in range(0, len(modlist.mods[mod[z]])):
                    if "crafted" in modlist.mods[mod[z]][x]:
                        explicitstat = modlist.mods[mod[z]][x]
                min = value[z]
                parameters["query"]["stats"][0]["filters"].append({"id": explicitstat, "value": {"min": min}})
        else:
            if mod[z] in modlist.mods:

                for x in range(0, len(modlist.mods[mod[z]])):
                    if "explicit" in modlist.mods[mod[z]][x]:
                        explicitstat = modlist.mods[mod[z]][x]
                min = value[z]
                parameters["query"]["stats"][0]["filters"].append({"id": explicitstat, "value": {"min": min}})
            #addfiltermods["filters"].update(addmod)
        z = z + 1



    #jprint(parameters)
    #addfilter["stats"].update(addfiltermods)
    #parameters["query"].update(addfilter)

def buildcurrency(itemparse):
    global parameters
    global name
    want = currency.CURRENCY[itemparse.splitlines()[1] ]
    
        
    parameters = {
        "exchange": {
            "status": {
                "option": "online"
            },
            "have": ["chaos"],
            "want": [want]
        }
    }
    name = parameters['exchange']['want']
    
def buildnormal(itemparse):
    global parameters
    global name
    itemlvl = itemparse.splitlines()[4]
    itemlvl = re.sub(r"[^0-9-.]", "", itemlvl)

    parameters = {
        "query": {
            "filters": {
                "misc_filters": {
                    "filters": {
                        "ilvl": {
                            "min": itemlvl,
                        }
                    }
                }
            },
            "status": {
                "option": "online"
            },
            "term": itemparse.splitlines()[1],
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

def buildmap(itemparse):
    global parameters
    global name
    splitmap = itemparse.splitlines()
    first = splitmap.index("--------")
    splitmap = itemparse.splitlines()[4].split()
    if "Blighted" in itemparse:
        parameters = {
            "query": {
                "status": {
                    "option": "online"
                },
                "term": itemparse.splitlines()[first-1],
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
    else:
        parameters = {
            "query": {
                "status": {
                    "option": "online"
                },
                "type": {
                    "option": itemparse.splitlines()[first-1]
                },
                "stats": [{
                    "type": "and",
                    "filters": []
                }]
            },
            "sort": {
                "price": "asc"
            }
        }
        name = parameters['query']['type']['option']


def buildgem(itemparse):
    global parameters
    global name
    qual = 0
    if "Quality:" in itemparse.splitlines()[6].split()[0]:
        qual = itemparse.splitlines()[6].split()[1].replace('+', '')
        qual = qual.replace('%', '')
    elif "Quality:" in itemparse.splitlines()[7].split()[0]:
        qual = itemparse.splitlines()[7].split()[1].replace('+', '')
        qual = qual.replace('%', '')
    elif "Quality:" in itemparse.splitlines()[8].split()[0]:
        qual = itemparse.splitlines()[8].split()[1].replace('+', '')
        qual = qual.replace('%', '')
    elif "Quality:" in itemparse.splitlines()[9].split()[0]:
        qual = itemparse.splitlines()[9].split()[1].replace('+', '')
        qual = qual.replace('%', '')




    parameters = {
        "query": {
            "status": {
                "option": "online"
            },
            "type": itemparse.splitlines()[1],
            "stats": [{
                "type": "and",
                "filters": []
            }],
            "filters": {
                "misc_filters": {
                    "filters": {
                        "gem_level": {
                            "min": itemparse.splitlines()[4].split()[1],
                            "max": itemparse.splitlines()[4].split()[1],
                        },
                        "quality": {
                            "min": qual,
                            "max": qual,
                        },
                        "corrupted": {
                            "option": checkifcurrepted(itemparse)
                        }

                    }
                }
            }
        },
        "sort": {
            "price": "asc"
        }
    }
    name = "{} Lvl: {} Qual: {} Corrupted {}".format(parameters['query']['type'], itemparse.splitlines()[4].split()[1], qual, checkifcurrepted(itemparse))

def searchweb(query):
    webbrowser.open("https://www.pathofexile.com/trade/search/Standard/"+ query)

def searchnewrare(mod, value, MessFrame):
    x = 0
    parameters["query"]["stats"][0]["filters"].clear()
    for k in mod:
        #print(mod[x].get())
        #print(value[x].get())

        if mod[x].get() in modlist.mods:
            for y in range(0, len(modlist.mods[mod[x].get()])):
                if "explicit" in modlist.mods[mod[x].get()][y]:
                    explicitstat = modlist.mods[mod[x].get()][y]
            min = value[x].get()


            parameters["query"]["stats"][0]["filters"].append({"id": explicitstat, "value": {"min": min}})
        #addfiltermods["filters"].update(addmod)

        x = x + 1
    MessFrame.destroy()
    buildpricewindow()


def buildpricewindow():
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

    #jprint(parameters)
    response = requests.post("https://www.pathofexile.com/api/trade/search/Standard", json=parameters)
    #jprint(response.json())
    try:
        if response.json()["total"] > 0:
            query = response.json()["id"]
            result = response.json()["result"][:10]
            #result = re.sub('[!@#$]', '', result)
            result = json.dumps(result)
            result = result.replace('[', '')
            result = result.replace(']', '')
            result = result.replace('"', '')
            result = result.replace(' ', '')

        #print("https://www.pathofexile.com/api/trade/fetch/{}?query={}".format(result, query))

            response = requests.get("https://www.pathofexile.com/api/trade/fetch/{}?query={}".format(result, query))
            result = response.json()["result"]
            #jprint(result)

            r = 0
            wr = {}

            pricecheckframe = tk.Tk()
            
            pricecheckframe.configure(background=config['colors']['bgcolor'])
            #pricecheckframe.geometry('300x200+200+200')
            pricecheckframe.title(name)

            for d in result:
                if d['listing']['price'] != None:
                    amount = d['listing']['price']['amount']
                    currency = d['listing']['price']['currency']
                    mods = "None"
                    if d['item']['identified'] is True and 'explicitMods' in d['item']:
                        mods = "\n".join(d['item']['explicitMods'])
                    if 'corrupted' in d['item']:
                        wr[r] = tk.Label(pricecheckframe, text="price {} {} Corrupted".format(amount, currency),
                                         fg=config['colors']['textcolor'], bg=config['colors']['bgcolor'])
                        wr[r].grid(row=r)
                        CreateToolTip(wr[r], mods)
                       
                    else:
                        wr[r] = tk.Label(pricecheckframe, text="price {} {}".format(amount, currency),
                                         fg=config['colors']['textcolor'], bg=config['colors']['bgcolor'])
                        wr[r].grid(row=r)
                        CreateToolTip(wr[r], mods)
                    r = r + 1

            B = tk.Button(pricecheckframe, text ="Close", command=lambda: pricecheckframe.destroy())
            B.grid(row=r)
            pricecheckframe.call('wm', 'attributes', '.', '-topmost', '1')
            pricecheckframe.mainloop()
        else:
            e = {}
            ev = {}

            response = requests.post("https://www.pathofexile.com/api/trade/search/Standard", json=parameters)
            query = response.json()["id"]

            MessFrame = tk.Tk()
            MessFrame.configure(background=config['colors']['bgcolor'])
            MessFrame.geometry('400x300+200+200')
            tk.Label(MessFrame, text="No result's Found", fg=config['colors']['textcolor'], bg=config['colors']['bgcolor']).grid(row=0, column=0, columnspan=2)
            x = 0
            for k in mod:
                e[x] = tk.Entry(MessFrame, width=40, fg=config['colors']['fgcolor'], bg=config['colors']['bgcolor'])
                e[x].insert(0, mod[x])
                e[x].grid(row=x+1, column=0)
                ev[x] = tk.Entry(MessFrame, width=5, fg=config['colors']['fgcolor'], bg=config['colors']['bgcolor'])
                ev[x].insert(0, value[x])
                ev[x].grid(row=x+1, column=1)
                x = x + 1
            tk.Button(MessFrame, text="Search Again", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'],
                                  command=lambda: searchnewrare(e, ev, MessFrame)).grid(row=x+1, column=0)
            tk.Button(MessFrame, text="Search on Web", bg=config['colors']['bgcolor'], fg=config['colors']['fgcolor'],
                                  command=lambda: searchweb(query)).grid(row=x+2, column=0)
            MessFrame.call('wm', 'attributes', '.', '-topmost', '1')
            MessFrame.mainloop()
    except:
        MessFrame = tk.Tk()
        MessFrame.configure(background=config['colors']['bgcolor'])
        MessFrame.geometry('150x50+200+200')
        MessFrame.title("Pricecheck")
        tk.Label(MessFrame, text="No result's Found", fg=config['colors']['textcolor'], bg=config['colors']['bgcolor']).grid(row=0, column=0, columnspan=2)
        MessFrame.call('wm', 'attributes', '.', '-topmost', '1')
        MessFrame.mainloop()
        
        
def buildpricewindowcurrency():
    #jprint(parameters)
    response = requests.post("https://www.pathofexile.com/api/trade/exchange/Standard", json=parameters)
    #jprint(response.json())
   
    
    query = response.json()["id"]
    result = response.json()["result"][:10]
    #result = re.sub('[!@#$]', '', result)
    result = json.dumps(result)
    result = result.replace('[', '')
    result = result.replace(']', '')
    result = result.replace('"', '')
    result = result.replace(' ', '')

    #print("https://www.pathofexile.com/api/trade/fetch/{}?query={}&exchange".format(result, query))

    response = requests.get("https://www.pathofexile.com/api/trade/fetch/{}?query={}&exchange".format(result, query))
    result = response.json()["result"]
    #print("https://www.pathofexile.com/api/trade/fetch/{}?query={}&exchange".format(result, query))
    #jprint(result)

    r = 0
    wr = {}

    pricecheckframe = tk.Tk()
    
    pricecheckframe.configure(background=config['colors']['bgcolor'])
    #pricecheckframe.geometry('300x200+200+200')
    pricecheckframe.title(name)

    for d in result:
        if d['listing']['price'] != None:
            amount = d['listing']['price']['exchange']['amount']
            currency = d['listing']['price']['exchange']['currency']
            whichamount = d['listing']['price']['item']['amount']
            whichcurrency = d['listing']['price']['item']['currency']
            wr[r] = tk.Label(pricecheckframe, text="{} {} -> {} {}".format(whichamount, whichcurrency, amount, currency),
                                fg=config['colors']['textcolor'], bg=config['colors']['bgcolor'])
            wr[r].grid(row=r)
            r = r + 1

    B = tk.Button(pricecheckframe, text ="Close", command=lambda: pricecheckframe.destroy())
    B.grid(row=r)
    pricecheckframe.call('wm', 'attributes', '.', '-topmost', '1')
    pricecheckframe.mainloop()
     
    