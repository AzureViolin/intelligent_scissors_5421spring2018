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
import time

class IntelligentScissor():

    def __init__(self, img, seed):

        '''
        @img: numpy array
        @seed: [row,column]
        '''
        #TODO more elegent way to switch row & column
        seed = (seed[1], seed[0])

        self.height = img.shape[0]
        self.width = img.shape[1]
        self.img = img.reshape(self.height, self.width, -1).astype(np.float32)
        self.dim = self.img.shape[2]
        self.pad_img = np.lib.pad(self.img, ((1,1),(1,1),(0,0)), 'constant', constant_values=0)
        self.seed = seed

        #self.states = np.zeros((self.height, self.width),
                #dtype=np.int32)  # 0 INITIAL, 1 ACTIVE, 2 EXPANDED
        #self.costs = np.zeros((self.height, self.width),
                #dtype=np.float32)
        self.link_cost = np.zeros((self.height, self.width, 8),
                dtype=np.float32)
        self.cost_graph=np.zeros((self.height*3, self.width*3, self.dim),
                dtype=np.float32)
        #self.prev_dict = {}
        self.node_dict = {}

        self.INITIAL =0
        self.ACTIVE  =1
        self.EXPAND  =2

        self.pq = heapdict()
        self.pq[self.coordinate2key(self.seed)] = 0
        self.link_calculation()
        #self.prev_dict[self.coordinate2key(self.seed)]=None
        #self.set_cost(self.seed, 0)

    def coordinate2key(self, pose):
        #return str(pose[0]).zfill(3)+'_'+str(pose[1]).zfill(3)
        return str(pose[0])+'_'+str(pose[1])

    def key2coordinate(self, key):
        coor = key.split("_")
        return (int(coor[0]), int(coor[1]))

    #def get_state(self, pose):
        #return self.states[pose[0]][pose[1]]

    #def set_state(self, pose, state):
        #self.states[pose[0]][pose[1]] = state

    #def set_cost(self, pose, cost):
        #self.costs[pose[0]][pose[1]] = cost

    def get_path(self, pose):
        path = []
        #TODO more elegent way to switch row & column
        path.append(pose)
        pose = (pose[1],pose[0])
        #next_pose = pose
        pose_key = self.coordinate2key(pose)
        while self.node_dict[pose_key].prev_node != None:
            new_pose_key = self.node_dict[pose_key].prev_node 
            new_pose_node = self.node_dict[new_pose_key]
            new_pose = self.key2coordinate(new_pose_key)
            path.append((new_pose[1],new_pose[0]))
            #cv2.line(self.img,
                    #(next_pose[1],next_pose[0]),
                    #(new_pose[1],new_pose[0]),
                    #(255,0,0))
            #next_pose = new_pose
            #next_pose_key = new_pose_node.prev_node
            pose_key = new_pose_key
        #cv2.imwrite("../output/path.png", self.img)
        return path

    def link_calculation(self):

        up_down = self.pad_img[:-2,:,:] - self.pad_img[2:,:,:]
        link_cost_0 = np.abs(up_down[:,1:-1,:] + up_down[:,2:,:])/4
        self.link_cost[:,:,0] = np.sqrt(np.sum(link_cost_0**2, axis=2)/self.dim)

        left_right = self.pad_img[:,:-2,:] - self.pad_img[:,2:,:]
        link_cost_6 = np.abs(left_right[1:-1,:,:] + left_right[2:,:,:])/4
        self.link_cost[:,:,6] = np.sqrt(np.sum(link_cost_6**2, axis=2)/self.dim)

        link_cost_1 = np.abs(self.pad_img[:-2,1:-1,:]-self.pad_img[1:-1,2:,:])/np.sqrt(2)
        self.link_cost[:,:,1] = np.sqrt(np.sum(link_cost_1**2, axis=2)/self.dim)

        link_cost_7 = np.abs(self.pad_img[1:-1,2:,:]-self.pad_img[2:,1:-1,:])/np.sqrt(2)
        self.link_cost[:,:,7] = np.sqrt(np.sum(link_cost_7**2, axis=2)/self.dim)

        self.link_cost[ :,   1:,  4] = self.link_cost[ :,   :-1,  0]
        self.link_cost[1:,    :,  2] = self.link_cost[ :-1, :,    6]
        self.link_cost[1:,   1:,  3] = self.link_cost[ :-1, :-1,  7]
        self.link_cost[ :-1, 1:,  5] = self.link_cost[1:,   :-1,  1]

        link_length = np.array([1,np.sqrt(2),1,np.sqrt(2),1,np.sqrt(2),1,np.sqrt(2)])
        self.link_cost = ((np.max(self.link_cost)-self.link_cost)*link_length)/2
        self.cost_graph[1::3,2::3,:]=self.link_cost[:,:,:1]\
                +np.zeros(self.dim)
        self.cost_graph[ ::3,2::3,:]=self.link_cost[:,:,1:2]\
                +np.zeros(self.dim)
        self.cost_graph[ ::3,1::3,:]=self.link_cost[:,:,2:3]\
                +np.zeros(self.dim)
        self.cost_graph[ ::3, ::3,:]=self.link_cost[:,:,3:4]\
                +np.zeros(self.dim)
        self.cost_graph[1::3, ::3,:]=self.link_cost[:,:,4:5]\
                +np.zeros(self.dim)
        self.cost_graph[2::3, ::3,:]=self.link_cost[:,:,5:6]\
                +np.zeros(self.dim)
        self.cost_graph[2::3,1::3,:]=self.link_cost[:,:,6:7]\
                +np.zeros(self.dim)
        self.cost_graph[2::3,2::3,:]=self.link_cost[:,:,7:8]\
                +np.zeros(self.dim)
        self.cost_graph[1::3,1::3,:]=self.img
        #cv2.imwrite("../output/cost_graph.png",self.cost_graph)
        return self.cost_graph

    #def cost_map_generation(self):
        #start = time.time()
        #while len(self.pq)>0:
            #prev_pop = self.pq.popitem() # time consuming part
            #prev_node_key = prev_pop[0]
            #prev_cost = prev_pop[1]
            #prev_node = self.key2coordinate(prev_node_key) # time consuming
            #self.set_state(prev_node, self.EXPAND) # time consuming part
            #prev_link_cost = self.link_cost[prev_node[0]][prev_node[1]]
            #for (i,n_pose) in enumerate(self.get_neighbor_nodes(prev_node)):
                #if n_pose[0]>=0 and n_pose[0]<self.height and \
                        #n_pose[1]>=0 and n_pose[1]<self.width:
                    #n_pose_state = self.get_state(n_pose)
                    #n_pose_key = self.coordinate2key(n_pose)
                    #if n_pose_state==self.INITIAL:
                        #self.set_state(n_pose, self.ACTIVE)
                        #self.pq[n_pose_key]=prev_cost+prev_link_cost[i]
                        ##self.set_cost(n_pose, prev_cost+prev_link_cost[i])
                        #self.prev_dict[n_pose_key]=prev_node
                    #elif n_pose_state==self.ACTIVE:
                        #if self.pq[n_pose_key]>\
                                #prev_cost+prev_link_cost[i]:
                            #self.pq[n_pose_key]=\
                                    #prev_cost+prev_link_cost[i]
                            #self.prev_dict[n_pose_key]=prev_node
                            ##self.set_cost(n_pose, prev_cost+prev_link_cost[i])
            ##break
        #end = time.time()
        #print ("total map time", end-start)
        #cv2.imwrite("../output/costs2.png", self.costs/np.max(self.costs)*255)


    def cost_map_generation(self):
        while len(self.pq)>0:
            prev_pop = self.pq.popitem()
            prev_node_key = prev_pop[0]
            prev_cost = prev_pop[1]

            prev_node_obj = self.node_dict[prev_node_key]
            prev_node_obj.state = self.EXPAND
            self.node_dict[prev_node_key] = prev_node_obj
            for n_pose in prev_node_obj.neighbours:
                n_pose_node = self.node_dict[n_pose[0]]
                n_pose_state = n_pose_node.state
                new_cost = prev_cost+n_pose[1]
                if n_pose_state==self.INITIAL:
                    self.pq[n_pose[0]]=new_cost
                    n_pose_node.state = self.ACTIVE
                    n_pose_node.prev_node = prev_node_key
                    self.node_dict[n_pose[0]]=n_pose_node
                elif n_pose_state==self.ACTIVE:
                    if self.pq[n_pose[0]]>new_cost:
                        self.pq[n_pose[0]]=new_cost
                        n_pose_node.prev_node = prev_node_key
                        self.node_dict[n_pose[0]]=n_pose_node
        
        #end = time.time()
        #print ("total map time", end-start_all)
        #cv2.imwrite("../output/costs2.png", self.costs/np.max(self.costs)*255)

    #def get_neighbor_nodes(self, pose):
        #row = pose[0]
        #column = pose[1]
        #return [(row  ,  column+1),
                #(row-1,  column+1),
                #(row-1,  column  ),
                #(row-1,  column-1),
                #(row  ,  column-1),
                #(row+1,  column-1),
                #(row+1,  column  ),
                #(row+1,  column+1)]

    def get_neighbor_node_keys(self, pose, link_cost):
        row = pose[0]
        column = pose[1]
        return [[self.coordinate2key((row  ,  column+1)), link_cost[0]],
                [self.coordinate2key((row-1,  column+1)), link_cost[1]],
                [self.coordinate2key((row-1,  column  )), link_cost[2]],
                [self.coordinate2key((row-1,  column-1)), link_cost[3]],
                [self.coordinate2key((row  ,  column-1)), link_cost[4]],
                [self.coordinate2key((row+1,  column-1)), link_cost[5]],
                [self.coordinate2key((row+1,  column  )), link_cost[6]],
                [self.coordinate2key((row+1,  column+1)), link_cost[7]]]

    def generate_all_node_dict(self):
        for i in range(1,self.height-1):
            for j in range(1,self.width-1):
                self.node_dict[self.coordinate2key((i,j))]=\
                        PQ_Node(None, self.INITIAL, self.get_neighbor_node_keys((i,j), self.link_cost[i][j]))
        # Initial all the border point as EXPAND
        for i in [0, self.height-1]:
            for j in range(self.width):
                self.node_dict[self.coordinate2key((i,j))]=\
                        PQ_Node(None, self.EXPAND, None)
        for i in range(self.height):
            for j in [0, self.width-1]:
                self.node_dict[self.coordinate2key((i,j))]=\
                        PQ_Node(None, self.EXPAND, None)

class PQ_Node():
    def __init__(self, prev_node, state, neighbours):
        self.prev_node = prev_node
        self.state = state
        self.neighbours = neighbours

if __name__=="__main__":
    import cv2
    img = cv2.imread("../images/test2.jpg", cv2.IMREAD_GRAYSCALE)
    #img = cv2.imread("../images/test3.jpeg")
    #img = cv2.resize(img, (15,15))
    seed = (240,199)
    obj = IntelligentScissor(img, seed)
    obj.link_calculation()
    start = time.time()
    obj.generate_all_node_dict()
    print ("node dict time:", time.time()-start)
    start = time.time()
    obj.cost_map_generation()
    print ("cost map time:", time.time()-start)
    obj.get_path((266,165))
