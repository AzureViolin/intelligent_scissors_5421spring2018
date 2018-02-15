#!/usr/bin/env python
# coding=utf-8
'''
Author:Tai Lei
Date:Do 15 Feb 2018 09:30:40 CST
Info:
'''

import numpy as np
import queue
import cv2


class IntelligentScissor():

    def __init__(self, img, seed):
        
        '''
        @img: numpy array 
        @seed: [x,y] 
        '''

        self.img= img
        self.height = img.shape[0]
        self.width = img.shape[1]
        self.seed = seed
        self.states = np.zeros((self.height, self.width), 
                dtype=np.int32)  # 0 INITIAL, 1 ACTIVE, 2 EXPANDED
        self.costs = np.zeros((self.height, self.width), 
                dtype=np.int32) 
        
        self.INITIAL =0
        self.ACTIVE  =1
        self.EXPAND  =2
        
        self.pq = queue.PriorityQueue()
        # TODO put seed to the queue

    def link_cost(self, (x, y)):
        pass 
    
    def get_state(self, (row, column)):
        return self.states[row][column]
    
    def set_state(self, (row, column), state):
        self.states[row][column] = state
    
    def make_node(self):
        #add linkcost
        #add state as ACTIVE
        #total cost equal to 
        pass

    def graph_generation(self):
        self.pq.put() # put seed to pq
        while self.pq.size()>0:
            new_node = self.pq.get()
            
            self.set_state(next_node.pose, self.EXPAND) # set 
            new_node.state = self.EXPAND

            for n_pose in self.get_neighbor_nodes(new_node.pose):
                if self.get_state(n_pose)==self.INITIAL:
                    next_node = self.make_node()  
                    # TODO add new node to pq
                elif self.get_state(n_pose)==self.ACTIVE: 
                    # TODO update value in pq

    def get_neighbor_nodes=(self, (row,column):
        return [(row-1, column-1),
                (row,   column-1),
                (row+1, column-1),
                (row-1, column),
                (row+1, column),
                (row-1, column+1),
                (row,   column+1),
                (row+1, column+1)]

class PQ_Node():
    def __init__(linkCost, state, totalCost, prevNode, pose):
        #self.linkCost =None
        #self.state = 0 # initial
        self.totalCost = None 
        self.prevNode = None
        self.pose = None # (row,colum)
    
    def __cmp__(self, other):
        return cmp(self.totalCost, other.totalCost)

if __name__=="__main__":
    img = cv2.imread("../images/test.jpg")
    seed = [20,10]
    obj = IntelligentScissor(img, seed)
