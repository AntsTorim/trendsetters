# -*- coding: utf-8 -*-

import unittest
from numgame import NumGame


class TestTable(unittest.TestCase):

    def setUp(self):
        self.ng = NumGame(players=1, c=5)
        self.ng.set(2, 3)
        self.ng.set(1, 3)
        self.ng.setforplayer(player=0, c=1, area=1)
        
    def test_board(self):
        ng = self.ng
        self.assertEqual(1, ng.board[2][3])
        self.assertEqual(ng.colfreqs().tolist(), [0, 1, 0, 2, 0])
        self.assertEqual(ng.rowweights().tolist(), [0, 3, 2, 0])
        ng.setforking(c=0)
        self.assertEqual(ng.colfreqs().tolist(), [2, 1, 0, 2, 0])
        self.assertEqual(ng.rowweights().tolist(), [2, 3, 2, 0])


    def test_cards(self):
        areaselection = set()
        abilityselection = set()
        #print(self.ng.areadeck)
        #print(self.ng.abilitydeck)
        for i in range(20):
            a = self.ng.hiddenarea()
            c = self.ng.hiddenability()
            self.assert_(a in [0, 1, 2, 3])
            self.assert_(c in [0, 1, 2, 3, 4])
            areaselection.add(a)
            abilityselection.add(c)
            self.ng.poparea()
            self.ng.popability()
        self.assertEqual(areaselection, {0, 1, 2, 3})
        self.assertEqual(abilityselection, {0, 1, 2, 3, 4})
        
    def test_buy(self):
        a_change = False
        c_change = False
        for i in range(10):
            a = self.ng.hiddenarea()
            c = self.ng.hiddenability()
            r = self.ng.find_row(0, a)
            if self.ng.board[r][c] == 1:
                hasAlready = True
            else:
                hasAlready = False
            old_cfreq = self.ng.colfreqs()[c]
            self.ng.buy(player=0)
            new_cfreq = self.ng.colfreqs()[c]
            if hasAlready:
                self.assertEqual(new_cfreq, old_cfreq)
            elif a == 0:
                self.assertEqual(new_cfreq, old_cfreq+2)
            else:
                self.assertEqual(new_cfreq, old_cfreq+1)
            if self.ng.hiddenarea() != a:
                a_change = True
            if self.ng.hiddenability() != c:
                c_change = True
        self.assert_(a_change)
        self.assert_(c_change)
            


class TestAuctionPhase(unittest.TestCase):
    
 
    def setUp(self):
        self.ng = NumGame(players=3, c=5)
        self.phase = self.ng.currentphase
        
    def test(self):
        self.assertEqual(self.ng.currentphase.type, "auction")
        self.assertEqual(self.ng.auctionstarter, 0)
        self.assertEqual(self.phase.activeplayer, 0)
        self.assertEqual(self.phase.checked, [])
        item = self.phase.item

        funds0 = self.ng.playerfunds[0]
        self.assert_(self.phase.can_check())
        area = self.phase.check()
        self.assert_(area in [0, 1, 2, 3])
        funds1 = self.ng.playerfunds[0]
        self.assertEqual(funds1, funds0 - self.phase.CHECK_COST)
        self.assertEqual(self.phase.checked, [0])
        
        self.assert_(self.phase.can_hide())
        self.phase.hide()
        funds2 = self.ng.playerfunds[0]
        self.assertEqual(funds2, funds1 - self.phase.HIDE_COST)
        self.assert_(self.phase.hidden)
        
        self.assertEquals(self.phase.highest_bid, 0)
        self.phase.bid(1700)
        funds3 = self.ng.playerfunds[0]
        self.assertEqual(funds3, funds2 - 1700)
        self.assertEqual(self.phase.highest_bid, 1700)
        self.assertEqual(self.phase.highest_bidder, 0)
        self.assertEqual(self.phase.activeplayer, 1)
        self.assert_(self.phase.active)
        
        self.assertFalse(self.phase.can_check())
        self.phase.pass_bid()
        self.assertEqual(self.phase.highest_bid, 1700)
        self.assertEqual(self.phase.highest_bidder, 0)
        self.assertEqual(self.phase.activeplayer, 2)
        self.assert_(self.phase.active)
        
        self.phase.bid(3000)
        self.assertEqual(self.phase.highest_bid, 3000)
        self.assertEqual(self.phase.highest_bidder, 2)
        self.assertFalse(self.phase.active)
        self.assert_(self.ng.has(2, area, item))
        
        self.ng.nextphase()
        self.assertEqual(self.ng.currentphase.type, "payday")
        self.assertFalse(self.ng.currentphase.active)
        
        self.ng.nextphase()
        self.assertEqual(self.ng.auctionstarter, 1)
        self.assertEqual(self.ng.currentphase.type, "auction")
        self.assert_(self.ng.currentphase.active)
        
        

unittest.main()