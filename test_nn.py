# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 16:17:46 2015

@author: Ants Torim
"""


import unittest
from nn import *

class TestBackprop(unittest.TestCase):
    
    def test_xor(self):
        """
        Train and test ANN to recognize XOR pattern 
        """
        xor_net = ANN.generated_net(2, 5, 1)
        self.assertEqual(2, len(xor_net.conn_list))
        xor_net_rnd = ANN.generated_net(2, 5, 1, rnd=True)
        self.assertEqual(2, len(xor_net_rnd.conn_list))
        patterns = [([0., 0.], [0.]),
                    ([0., 1.], [1.]),
                    ([1., 0.], [1.]),
                    ([1., 1.], [0.])]
        print(xor_net_rnd.conn_list)
        for i in range(500):
            for in_pattern, target in patterns: 
                xor_net_rnd.backprop(np.array(in_pattern), np.array(target), alfa=25)
        for in_pattern, target in patterns:
            print(in_pattern, xor_net_rnd.out_vector(np.array(in_pattern)))
            #self.assertAlmostEqual(target, xor_net.out_vector(in_pattern)[0], 1)

if __name__ == "__main__":
    unittest.main()        
        