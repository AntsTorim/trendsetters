# -*- coding: utf-8 -*-

import numpy as np
from game import *

class NumGame(Game):

       

    def emptyboard(self):
        self.board = np.zeros((self.r, self.c))

    def set(self, r, c, val=1):
        self.board[r, c] = val
   
 
    def colfreqs(self):
        return np.dot(np.ones(self.r), self.board) + self.board[0]
        
    def rowweights(self):
        substituted = self.board * self.colfreqs()
        return np.dot(substituted, np.ones(self.c))


if __name__ == "__main__":
    ng = NumGame(2)
    print(repr(ng))
    ng.currentphase.bid(1000)    
    print(repr(ng))
    ng.currentphase.pass_bid()    
    print(repr(ng))
    ng.nextphase()
    print(repr(ng))
    ng.nextphase()
    print(repr(ng))
    ng.currentphase.check()    
    print(repr(ng))
    ng.currentphase.hide()  
    print(repr(ng))
    ng.currentphase.pass_bid()
    print(repr(ng))


