# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 13:31:01 2015

@author: Ants Torim
"""

import random


class Game:
    """
    Entire game, from start to end
    """    
    
    
    def __init__(self, players, c=9, areas=3, startfunds=10000):
        """
        Initialize game with number of players, c columns 
        and number of areas. Call emptyboard() to create 
        empty board (first row is for the King).
        Call initdecks() to create full area and ability decks 
        (self.areadeck, self.abilitydeck).
        """
        self.players = players
        self.areas = areas
        self.r = players*areas + 1
        self.c = c
        self.auctionstarter = 0
        self.emptyboard()
        self.initdecks()
        self.playerfunds = [startfunds] * self.players
        self.currentphase = AuctionPhase(self)
        
    def emptyboard(self):
        """
        Creates empty board
        """
        raise NotImplementedError
        
    def initdecks(self):
        self.areadeck = list(range(self.areas+1)) * self.c
        self.abilitydeck = list(range(self.c)) * (self.areas+1)
        random.shuffle(self.areadeck)
        random.shuffle(self.abilitydeck)
        
    def find_row(self, player, area):
        """
        Returns row index for player/area combination
        player: 0.. self.players-1
        area: 0.. self.areas (0 is the King)
        """    
        if area == 0:
            return 0
        else:
            return player + (area-1) * self.players + 1
    
    def setforplayer(self, player, area, c, val=1):
        """
        Sets ability c for the player in area
        """
        self.set(self.find_row(player, area), c, val)
   
    def setforking(self, c, val=1):
        """
        Sets ability c for the King.
        """
        self.set(0, c, val)
        
    def hiddenarea(self): 
        """
        Returns hidden area code
        """
        return self.areadeck[0]
        
    def poparea(self): 
        """
        Returns hidden area code and replaces hiddenarea with new 
        """
        result = self.areadeck[0]
        del self.areadeck[0]
        return result
        
    def hiddenability(self): 
        """
        Returns hidden area code
        """
        return self.abilitydeck[0]
        
    def popability(self): 
        """
        Returns hidden area code and replaces hiddenarea with new 
        """
        result = self.abilitydeck[0]
        del self.abilitydeck[0]
        return result
        
    def buy(self, player):
        """
        Tries to give hidden ability to players band in hidden area,
        unless area is the King. 
        """
        if self.hiddenarea() > 0:
            self.setforplayer(player, self.hiddenarea(), self.hiddenability())
        else:
            self.setforking(self.hiddenability())
        self.poparea()
        self.popability()
        
    def has(self, player, area, ability):
        """
        Bool showing if player has ability in area.
        If area is 0 then checks for the King
        """
        r = self.find_row(player, area)
        return self.board[r][ability]


    def nextphase(self):
        """
        Move to next phase. Current should be inactive.
        """
        assert not self.currentphase.active
        if self.currentphase.type == "auction":
            self.currentphase = PaydayPhase(self)
        elif self.currentphase.type == "payday":
            self.auctionstarter = (self.auctionstarter + 1) % self.players
            self.currentphase = AuctionPhase(self)
    
        
class AuctionPhase:
    """
    One auction phase
    """
    
    def __init__(self, game):
        self.activeplayer = game.auctionstarter
        self.game = game
        self.CHECK_COST = 1000
        self.HIDE_COST = 1000
        self.BIDDING_STEP = 1000
        self.checked = [] # Players who have checked
        self.hidden = False
        self.winner = None
        self.highest_bid = 0
        self.highest_bidder = None
        self.active = True # If phase is active
        self.item = game.hiddenability()
        self.type = "auction"


# ---------- Player methods --------------------------------

    def can_check(self):
        return (self.playerfunds() >= self.CHECK_COST) and not self.hidden
        
    def check(self):
        """        
        Returns hidden area and deducts CHECK_COST from active_player
        """
        assert self.can_check()
        self.deduct(self.CHECK_COST)
        self.checked.append(self.activeplayer)
        return self.game.hiddenarea()
        
    def can_hide(self):
        return (self.playerfunds() >= self.HIDE_COST) and not self.hidden
        
    def hide(self):
        assert self.can_hide()
        self.deduct(self.HIDE_COST)
        self.hidden = True 
      
    def bid(self, bidsum):
        assert self.playerfunds() >= bidsum
        assert bidsum > (self.highest_bid + self.BIDDING_STEP)
        self.deduct(bidsum)
        self.highest_bid = bidsum
        self.highest_bidder = self.activeplayer
        self.nextplayer()
        
    def pass_bid(self):
        self.nextplayer()

 # -------------- Internal methods ------------------------------------
       
    def playerfunds(self):
        return self.game.playerfunds[self.activeplayer]

    def deduct(self, amount):
        self.game.playerfunds[self.activeplayer] -= amount

     
    def nextplayer(self):
        """
        Move to next player or finalize the phase
        """
        self.activeplayer = (self.activeplayer + 1) % self.game.players
        if self.activeplayer == self.game.auctionstarter:
            # Phase ends
            self.finalize()

    def finalize(self):
         self.active = False
         self.game.setforplayer(self.highest_bidder, 
                                self.game.poparea(),
                                self.game.popability())
         

class PaydayPhase:
    
    def __init__(self, game):
        self.game = game
        self.type = "payday"
        self.PAY = 2000
        game.playerfunds = [x + self.PAY for x in game.playerfunds]
        self.active = False

if __name__ == "__main__":
    pass