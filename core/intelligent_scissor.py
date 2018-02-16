#!/usr/bin/env python
# coding=utf-8
'''
Author:Tai Lei
Date:Do 15 Feb 2018 09:30:40 CST
Info:
'''

import numpy as np
import queue
import heapdict
import cv2

class IntelligentScissor():

    def __init__(self, img, seed):
        
        '''
        @img: numpy array 
        @seed: [x,y] 
        '''

        self.height = img.shape[0]
        self.width = img.shape[1]
        self.img = img.reshape(self.height, self.width, -1).astype(np.float32)
        self.dim = self.img.shape[2]
        self.pad_img = np.lib.pad(self.img, ((1,1),(1,1),(0,0)), 'reflect')
        self.seed = seed
        
        self.states = np.zeros((self.height, self.width), 
                dtype=np.int32)  # 0 INITIAL, 1 ACTIVE, 2 EXPANDED
        self.costs = np.zeros((self.height, self.width), 
                dtype=np.int32)+np.NAN 
        self.link_cost = np.zeros((self.height, self.width, 8), 
                dtype=np.int32)+np.NAN

        self.INITIAL =0
        self.ACTIVE  =1
        self.EXPAND  =2
        
        self.pq = heapdict.heapdict()
        self.node_dict = {}
        # TODO put seed to the queue
        # TODO set the margin point state to expanded
        self.pq[self.coordinate2key(self.seed)] = 0
        #self.node_dict[self.coordinate2key(self.seed)] = PQ_Node(
                
                #)

    #def generate_link_cost(self):
        #for row_ in xrange(self.height):
            #for column_ in xrange(self.width)
    
    def coordinate2key(self, pose):
        return str(pose[0])+'_'+str(pose[1])

    def get_state(self, pose):
        return self.states[pose[0]][pose[1]]
    
    def set_state(self, pose, state):
        self.states[pose[0]][pose[1]] = state
    
    def make_node(self):
        #add linkcost
        #add state as ACTIVE
        #total cost equal to 
        pass
    
    def link_calculation(self):
        
        upminusdown = self.pad_img[:-2,:,:] - self.pad_img[2:,:,:]
        link_cost_0 = ((upminusdown[:,1:-1,:] + upminusdown[:,2:,:]))/4
        self.link_cost[:,:,0] = np.sqrt(np.sum(link_cost_0**2, axis=2)/self.dim)
        
        leftminusright = self.pad_img[:,:-2,:] - self.pad_img[:,2:,:]
        link_cost_6 = ((leftminusright[1:-1,:,:] + leftminusright[2:,:,:]))/4
        self.link_cost[:,:,6] = np.sqrt(np.sum(link_cost_6**2, axis=2)/self.dim)
        
        link_cost_1 = (self.pad_img[:-2,2:,:] - self.pad_img[1:-1,1:-1,:])/np.sqrt(2)
        self.link_cost[:,:,1] = np.sqrt(np.sum(link_cost_1**2, axis=2)/self.dim)
        
        link_cost_7 = (self.pad_img[2:,2:,:] - self.pad_img[1:-1,1:-1,:])/np.sqrt(2)
        self.link_cost[:,:,7] = np.sqrt(np.sum(link_cost_7**2, axis=2)/self.dim)
        
        self.link_cost[:,  1:, 4] = self.link_cost[:,  :-1, 0]
        self.link_cost[:-1, :, 2] = self.link_cost[1:, :,   6]
        self.link_cost[1:, 1:, 3] = self.link_cost[:-1,:-1, 7]
        self.link_cost[:-1,1:, 5] = self.link_cost[1:, :-1, 1]

    def graph_generation(self):
        self.pq.put() # put seed to pq
        while self.pq.size()>0:
            new_node = self.pq.popitem()
            
            self.set_state(next_node.pose, self.EXPAND) # set 
            new_node.state = self.EXPAND

            for n_pose in self.get_neighbor_nodes(new_node.pose):
                # TODO check if n_pose is in the range
                if self.get_state(n_pose)==self.INITIAL:
                    next_node = self.make_node()  
                    # TODO add new node to pq
                elif self.get_state(n_pose)==self.ACTIVE: 
                    # TODO update value in pq
                    pass

    def get_neighbor_nodes(self, pose):
            row = pose[0]
            column = pose[1]
            return [(row,    column+1),
                    (row-1,  column+1),
                    (row-1,  column),
                    (row-1,  column-1),
                    (row,    column-1),
                    (row+1,  column-1),
                    (row+1,  column),
                    (row+1,  column+1)]

class PQ_Node():
    def __init__(linkCost, state, totalCost, prevNode, pose):
        self.linkCost =None
        self.state = 0 # initial
        self.prevNode = None
        self.pose = None # (row,colum)
    
    def __cmp__(self, other):
        return cmp(self.totalCost, other.totalCost)


if __name__=="__main__":
    #img = cv2.imread("../images/test.jpg", cv2.IMREAD_GRAYSCALE)
    img = cv2.imread("../images/test.jpg")
    img = cv2.resize(img, (3,3))
    seed = (5,4)
    obj = IntelligentScissor(img, seed)
    obj.link_calculation()
