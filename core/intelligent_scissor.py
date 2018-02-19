#!/usr/bin/env python
# coding=utf-8
'''
Author:Tai Lei
Date:Do 15 Feb 2018 09:30:40 CST
Info:
'''

import numpy as np
import queue
from heapdict import heapdict
import cv2
#import matplotlib.pyplot as plt

class IntelligentScissor():

    def __init__(self, img, seed):

        '''
        @img: numpy array
        @seed: [row,column]
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
                dtype=np.int32)
        #+np.NAN
        self.link_cost = np.zeros((self.height, self.width, 8),
                dtype=np.int32)+np.NAN

        self.INITIAL =0
        self.ACTIVE  =1
        self.EXPAND  =2

        self.pq = heapdict()
        self.prev_dict = {}
        self.pq[self.coordinate2key(self.seed)] = 0
        self.link_calculation()
        self.prev_dict[self.coordinate2key(self.seed)]=None
        self.set_cost(self.seed, 0)

    def coordinate2key(self, pose):
        return str(pose[0]).zfill(3)+'_'+str(pose[1]).zfill(3)

    def key2coordinate(self, key):
        return (int(key[:3]), int(key[-3:]))

    def get_state(self, pose):
        return self.states[pose[0]][pose[1]]

    def set_state(self, pose, state):
        self.states[pose[0]][pose[1]] = state

    def set_cost(self, pose, cost):
        self.costs[pose[0]][pose[1]] = cost

    def get_path(self, pose):
        path = []
        next_pose = pose
        path.append(next_pose)
        while self.prev_dict[self.coordinate2key(next_pose)] != None:
            new_pose = self.prev_dict[self.coordinate2key(next_pose)]
            path.append(new_pose)
            #cv2.line(self.img,
                    #(next_pose[1],next_pose[0]),
                    #(new_pose[1],new_pose[0]), 
                    #(255,0,0))
            next_pose = new_pose
        #cv2.imwrite("../images/path.png", self.img)
        return path 

    def link_calculation(self):

        upminusdown = np.abs(self.pad_img[:-2,:,:] - self.pad_img[2:,:,:])
        link_cost_0 = ((upminusdown[:,1:-1,:] + upminusdown[:,2:,:]))/4
        self.link_cost[:,:,0] = np.sqrt(np.sum(link_cost_0**2, axis=2)/self.dim)

        leftminusright = np.abs(self.pad_img[:,:-2,:] - self.pad_img[:,2:,:])
        link_cost_6 = ((leftminusright[1:-1,:,:] + leftminusright[2:,:,:]))/4
        self.link_cost[:,:,6] = np.sqrt(np.sum(link_cost_6**2, axis=2)/self.dim)

        link_cost_1 = np.abs(self.pad_img[:-2,2:,:]-self.pad_img[1:-1,1:-1,:])/np.sqrt(2)
        self.link_cost[:,:,1] = np.sqrt(np.sum(link_cost_1**2, axis=2)/self.dim)

        link_cost_7 = np.abs(self.pad_img[2:,2:,:]-self.pad_img[1:-1,1:-1,:])/np.sqrt(2)
        self.link_cost[:,:,7] = np.sqrt(np.sum(link_cost_7**2, axis=2)/self.dim)

        self.link_cost[ :,   1:,  4] = self.link_cost[ :,   :-1,  0]
        self.link_cost[ :-1,  :,  2] = self.link_cost[1:,   :,    6]
        self.link_cost[1:,   1:,  3] = self.link_cost[ :-1, :-1,  7]
        self.link_cost[ :-1, 1:,  5] = self.link_cost[1:,   :-1,  1]

    def graph_generation(self):
        while len(self.pq)>0:
            prev_pop = self.pq.popitem()
            prev_node_key = prev_pop[0]
            prev_cost = prev_pop[1]
            #print (prev_pop)
            prev_node = self.key2coordinate(prev_node_key)
            self.set_state(prev_node, self.EXPAND)
            prev_link_cost = self.link_cost[prev_node[0]][prev_node[1]]
            for (i,n_pose) in enumerate(self.get_neighbor_nodes(prev_node)):
                #print (n_pose, i)
                #print (self.height, self.width)
                if n_pose[0]>=0 and n_pose[0]<self.height and \
                        n_pose[1]>=0 and n_pose[1]<self.width:
                    if self.get_state(n_pose)==self.INITIAL:
                        self.set_state(n_pose, self.ACTIVE)
                        self.pq[self.coordinate2key(n_pose)]=\
                                prev_cost+prev_link_cost[i]
                        self.set_cost(n_pose, prev_cost+prev_link_cost[i])
                        self.prev_dict[self.coordinate2key(n_pose)]=prev_node
                    elif self.get_state(n_pose)==self.ACTIVE:
                        if self.pq[self.coordinate2key(n_pose)]>\
                                prev_cost+prev_link_cost[i]:
                            self.pq[self.coordinate2key(n_pose)]=\
                                    prev_cost+prev_link_cost[i]
                            self.prev_dict[self.coordinate2key(n_pose)]=prev_node
                            self.set_cost(n_pose, prev_cost+prev_link_cost[i])

        #print (self.costs)
        #print (np.max(self.costs))
        #plt.imshow(self.costs)
        #plt.show()
        #cv2.imwrite("../images/costs2.png", self.costs/np.max(self.costs)*255)

    def get_neighbor_nodes(self, pose):
        row = pose[0]
        column = pose[1]
        return [(row  ,  column+1),
                (row-1,  column+1),
                (row-1,  column  ),
                (row-1,  column-1),
                (row  ,  column-1),
                (row+1,  column-1),
                (row+1,  column  ),
                (row+1,  column+1)]

#class PQ_Node():
    #def __init__(self, prevNode):
        #self.prevNode = prevNode

if __name__=="__main__":
    #img = cv2.imread("../images/test2.jpeg", cv2.IMREAD_GRAYSCALE)
    img = cv2.imread("../images/test2.jpeg")
    #img = cv2.resize(img, (15,15))
    seed = (150,130)
    obj = IntelligentScissor(img, seed)
    obj.link_calculation()
    obj.graph_generation()
    obj.get_path((120,10))
