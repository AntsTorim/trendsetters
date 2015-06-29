# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 13:31:01 2015

@author: Ants Torim
"""

import random


class Game:
    """
    Entire game, from start to end
    
    Supports iteration:
    for phase, player in game:
       ...
    or 
    phase, player = next(game)
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
        self.winamount = c + c // 2 + 1
    

    def __iter__(self):
        """
        Generator that yields (phase, player) tuples until game ends. 
        Player actions should be carried out on those phases.
        Previous phases are finalized with default actions, if needed.
        """
        while self.winner() == None:
            phase = self.currentphase 
            player = self.currentphase.activeplayer
            yield phase, player
            phase.finalize_for(player)
            if not phase.active and not self.winner():
                self.nextphase()
                
            
                
            
    def emptyboard(self):
        """
        Creates empty board
        """
        raise NotImplementedError
    
    def set(self, r, c, val=1):
        """
        Sets r, c to val on board
        """
        raise NotImplementedError
        
    def colfreqs(self):
        """
        Column frequencies
        """
        raise NotImplementedError
        
    def rowweights(self):
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
    
    def rowinfo(self, row):
        """
        Returns (player, area) tuple
        """
        if row == 0:
            return (None, 0)
        else:
            return ((row-1) % (self.players), 1 + (row-1) // self.players)
    
    def setforplayer(self, player, area, c, val=1):
        """
        Sets ability c for the player in area(1...3)
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
        Game should have no winner yet.
        """
        assert not self.currentphase.active
        assert not self.winner()
        if self.currentphase.type == "auction":
            self.currentphase = PaydayPhase(self)
        elif self.currentphase.type == "payday":
            self.auctionstarter = (self.auctionstarter + 1) % self.players
            self.currentphase = AuctionPhase(self)
        
    def winner(self):
        """
        If game has ended returns the winner, else None
        """
        max_weight = -1
        max_player = None
        for i in range(len(self.rowweights())):
            w = self.rowweights()[i]
            if w > max_weight:
                max_weight = w
                max_player = i
        if max_weight >= self.winamount:
            return max_player
        elif len(self.abilitydeck)==0 or len(self.areadeck)==0:
            return max_player
        else:
            return None
        
    def __repr__(self):
        # Build board description
        board_desc = ".  ".join([str(x) for x in range(self.c)])
        board_desc = "   \t[ " + board_desc +  ".]\n\n"
        row_template = "{0}:\t{1}    {2}  \n"
        board_desc += row_template.format("K", self.board[0],
                                          self.rowweights()[0])
        for i in range(1, len(self.board)):
            player, _ = self.rowinfo(i)
            board_desc += row_template.format(player, self.board[i],
                                              self.rowweights()[i])
        board_desc += "\nC:\t" + str(self.colfreqs()) + "\n"
        
        # Build monetary description
        money_desc = ""
        money_list = [str(i) + ": " + str(self.playerfunds[i]) + "$"
            for i in range(self.players)]
        money_desc = ", ".join(money_list)
        
        return "Game\n{0}\n{1} \n\nPhase:  {2}".format(board_desc,
            money_desc, repr(self.currentphase))
        
        
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
        self.area = game.hiddenarea()
        self.type = "auction"
        self.steps = [AuctionStep(self.activeplayer)] # step history


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
        self.steps[-1].checked = True
        return self.game.hiddenarea()
        
    def can_hide(self):
        return (self.playerfunds() >= self.HIDE_COST) and not self.hidden
        
    def hide(self):
        assert self.can_hide()
        self.deduct(self.HIDE_COST)
        self.hidden = True 
        self.steps[-1].hid = True
      
    def bid(self, bidsum):
        assert self.playerfunds() >= bidsum
        assert bidsum >= (self.highest_bid + self.BIDDING_STEP)
        #self.deduct(bidsum)
        self.highest_bid = bidsum
        self.highest_bidder = self.activeplayer
        self.steps[-1].bid = bidsum
        self.nextplayer()
        
    def pass_bid(self):
        self.steps[-1].bid = None
        self.nextplayer()

    def finalize_for(self, player):
        "If player is activeplayer then pass bid, and move to next player"
        if player == self.activeplayer:
            self.pass_bid()
        
 # -------------- Internal methods ------------------------------------
       
    def playerfunds(self):
        return self.game.playerfunds[self.activeplayer]

    def deduct(self, amount, player=None):
        if player == None:
            player = self.activeplayer
        self.game.playerfunds[player] -= amount

     
    def nextplayer(self):
        """
        Move to next player or finalize the phase
        """
        self.activeplayer = (self.activeplayer + 1) % self.game.players
        if self.activeplayer == self.game.auctionstarter:
            # Phase ends
            self.finalize()
        else:
            self.steps.append(AuctionStep(self.activeplayer))

    def finalize(self):
         self.active = False
         self.winner = self.highest_bidder
         area = self.game.poparea()
         ability = self.game.popability()
         if self.highest_bidder != None:
             self.deduct(self.highest_bid, self.highest_bidder)
             self.game.setforplayer(self.highest_bidder, area, ability)
                                
    def __repr__(self):
        if self.active:
            activity_desc = "active"
        else:
            activity_desc = "inactive"
        if self.hidden:
            activity_desc += "/hidden"
        steps_desc = "\n\t".join([repr(x) for x in self.steps])
        if self.winner == None:
            player_desc = "active: " + str(self.activeplayer)
        else:
            player_desc = "winner: " + str(self.winner) + \
                ". For area " + str(self.area) + "."
        if self.activeplayer in self.checked:
            player_desc += ", checked area " + str(self.area)
        result = """Auction is {0}. For sale: {1}. Highest bid is {2}$.
        Player, {3}
        Steps: 
        {4}
        
         """.format(activity_desc, str(self.item), self.highest_bid,
                    player_desc, steps_desc)
        return result



class AuctionStep:
    """
    Data structure with overriden fieldwise equality:
    player
    checked (True / False)
    hid (True / False)
    bid (None if passed)
    """
    
    
    def __init__(self, player, checked=False, hid=False, bid=None):
        self.player = player
        self.checked = checked
        self.hid = hid
        self.bid = bid      
      
    def __eq__(self,other):
        return self.__dict__ == other.__dict__
        
    def __ne__(self, other):
        return not self == other
    
    def __repr__(self):
        if self.checked:
            checked_desc = "checked, "
        else:
            checked_desc = ""
        if self.hid:
            hid_desc = "hid,"
        else:
            hid_desc = ""
        result = "Player {0}, {1}{2} bid: {3}".format(self.player,
                                               checked_desc,
                                               hid_desc,
                                               self.bid)
        return result
        
            

class PaydayPhase:
    
    def __init__(self, game):
        self.activeplayer = None
        self.game = game
        self.type = "payday"
        self.PAY = 2000
        game.playerfunds = [x + self.PAY for x in game.playerfunds]
        self.active = False
        
    def finalize_for(self, player): pass

    def __repr__(self): return "Payday\n"
    
    

if __name__ == "__main__":
    pass