# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 19:59:27 2015

@author: Ants Torim
"""
import numpy as np
from numpy.random import rand
from scipy.special import expit as sigmoid


def sigmoid_delta(a):
    """
    Derviative of sigmoid applied to the vector a
    """
    return sigmoid(a) * (np.ones(len(a)) - sigmoid(a))

def transform(in_vector, conn_matrix):
    """
    Transform in_vector into out_vector using conn_matrix
    Last column of conn_matrix is bias
    """
    raw_out = conn_matrix.dot(np.append(in_vector, 1.0))
    return sigmoid(raw_out)
    
    

class ANN:
    """
    Feedforward artificial neural network
    """
    
    def __init__(self, conn_list):
        """
        conn_list is a list of weight matrices
        """
        self.conn_list = conn_list


    @classmethod
    def generated_net(cls, *layer_neurons, rnd=False):
        """
        Alternate constructor. 
        Arguments are numbers of neurons for in to out layers.
        Connection weights are zeros if rnd is False, 
        else random floats from -1 to 1.
        """
        assert len(layer_neurons) > 2
        conns = []
        in_n = layer_neurons[0]
        for out_n in layer_neurons[1:]:
            if rnd:
                conn_matrix = rand(out_n, in_n+1)*2 - np.ones([out_n, in_n+1])
            else:
                conn_matrix = np.zeros([out_n, in_n+1])
            conns.append(conn_matrix)
            in_n = out_n
        return cls(conns)
            


    def out_vector(self, in_vector):
        """
        ANN calculated out_vector from in_vector
        """ 
        layer_vector = in_vector
        for conn in self.conn_list:
            layer_vector = transform(layer_vector, conn)
            #print(layer_vector)
        return layer_vector
    
    
    def backprop(self, in_vector, target, alfa=0.5):
        """
        Backpropagate the net from example (in_vector, target)
        using learning rate alfa.
        """
        layer_vectors = [in_vector]
        for conn in self.conn_list:
            layer_vectors.append(transform(layer_vectors[-1], conn))
        #layer_vectors.reverse()
        diff = layer_vectors[-1] - target
        layer_weights = list(zip(layer_vectors, self.conn_list))
        for in_layer, weight_matrix in reversed(layer_weights): 
            #print(in_vector, weight_matrix)
            in_layer = np.append(in_layer, 1.0) # add bias node
            net_j = np.dot(weight_matrix, in_layer)
            #print(diff, net_j)
            sigma = diff  * sigmoid_delta(net_j)
            #print(in_layer, sigma)
            diff = np.dot(sigma, weight_matrix) [:-1]
            delta_w = - alfa * np.dot(np.array([sigma]).T, np.array([in_layer]))
            #print(delta_w)
            #print(weight_matrix)
            weight_matrix += delta_w
            #print(weight_matrix)
        
        
        
        
        
        
    
if __name__ == "__main__":
    in_mid = np.array([[0., 0., 0.],
                       [0., 1., 0.],
                       [0., 0., 0.]])
    mid_out = np.array([[1., 0., 0., 0.],
                        [0., 1., 0., 0.]])
    net = ANN([in_mid, mid_out])
    #print(net.out_vector(np.ones(2)))
    #print(net.out_vector(np.array([1, 0])))
    print(net.out_vector(np.ones(2)))
    for i in range(1000):
        net.backprop(np.array([0, 0]), np.array([0, 1]))
        net.backprop(np.array([1, 0]), np.array([0, 1]))
        net.backprop(np.array([0, 1]), np.array([0, 1]))
        net.backprop(np.array([1, 1]), np.array([1, 0]))
    print(net.out_vector(np.array([0, 0])))
    print(net.out_vector(np.array([1, 0])))
    print(net.out_vector(np.array([0, 1])))
    print(net.out_vector(np.array([1, 1])))
    
    