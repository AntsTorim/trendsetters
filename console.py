# -*- coding: utf-8 -*-
"""
Created on Sat May 23 17:47:41 2015

@author: Ants Torim
"""

from numgame import *

g = NumGame(3)

for phase, player in g:
    if phase.type == "auction" and phase.active:
        print(g)
        while True:
            a = input("Action(c=check, h=hide, b ___ = bid ___, p=pass): ")
            if a[0].lower() == "c":
                phase.check()
                print(g)
            elif a[0].lower() == "h":
                phase.hide()
                print(g)
            elif a[0].lower() == "b":
                phase.bid(int(a[1:]))
                break
            else:
                phase.pass_bid()
                break
    # show payday phase or results of complete auction phase 
    if phase.type == "payday" or not phase.active:
        print(g)
        a = input("Any key to continue...")
        
print(g)
print("Winner is: ", g.winner())
