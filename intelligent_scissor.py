#!/usr/bin/env python
# coding=utf-8
'''
Author:Tai Lei
Date:Do 15 Feb 2018 09:30:40 CST
Info:
'''

import numpy as np
import queue
from heapq import *
from collections import deque
import time
import copy
from PIL import Image

link2coor={0:(0,1), 1:(-1,1), 2:(-1,0), 3:(-1,-1), 4:(0,-1), 5:(1,-1), 6:(1,0), 7:(1,1)}


class IntelligentScissor():

    def __init__(self, img):

        '''
        @img: numpy array
        @seed: [row,column]
        '''
        self.height = img.shape[0]
        self.width = img.shape[1]
        self.img = img.reshape(self.height, self.width, -1).astype(np.float32)
        self.dim = self.img.shape[2]
        self.pad_img = np.lib.pad(self.img,
                ((1,1),(1,1),(0,0)), 'constant', constant_values=0)

        self.link_cost = np.zeros((self.height, self.width, 8),
                dtype=np.float32)
        self.cost_graph=np.zeros((self.height*3, self.width*3, self.dim),
                dtype=np.float32)
        self.pixel_node=np.zeros((self.height*3, self.width*3, self.dim),
                dtype=np.int32)
        self.path_tree=np.zeros((self.height*3, self.width*3),
                dtype=np.float32)

        self.node_dict = {}
        self.mask = np.zeros((self.height, self.width),dtype=np.int32)

        self.INITIAL =0
        self.ACTIVE  =1
        self.EXPAND  =2
        self.BORDER  =3
        self.link_calculation()
        self.generate_all_node_dict()
        self.contour_mask_list = []

    def coordinate2key(self, pose):
        return self.width*pose[0]+pose[1]

    def key2coordinate(self, key):
        return (key//self.width, key%self.width)

    def get_path(self, pose):
        path = []
        path.append(pose)
        pose = (pose[1],pose[0])
        pose_key = self.coordinate2key(pose)
        while self.node_dict[pose_key].prev_node != None:
            new_pose_key = self.node_dict[pose_key].prev_node[0]
            #new_pose_node = self.node_dict[new_pose_key]
            new_pose = self.key2coordinate(new_pose_key)
            path.append((new_pose[1],new_pose[0]))
            pose_key = new_pose_key
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

        self.pixel_node[1::3,1::3,:]=self.img
        link_length = np.array([1,np.sqrt(2),1,np.sqrt(2),1,np.sqrt(2),1,np.sqrt(2)])
        self.link_cost = ((np.max(self.link_cost)-self.link_cost)*link_length)/2
        self.cost_graph[1::3,1::3,:]=self.link_cost[:,:,:1]\
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
        return self.cost_graph

    def path_tree_generation(self):
        self.update_node_dict()
        pathtree_q=deque()
        seed_key = self.coordinate2key((1, 1))
        pathtree_q.append(seed_key)
        node_dict = copy.deepcopy(self.node_dict)

        while len(pathtree_q) > 0:
            root_key = pathtree_q.popleft()
            root_node = node_dict[root_key]
            prev_node_pair = root_node.prev_node

            for n_pose in root_node.neighbours:
                n_pose_node = node_dict[n_pose[0]]
                n_pose_state = n_pose_node.state
                if n_pose_state == self.INITIAL:
                    pathtree_q.append(n_pose[0])
                    n_pose_node.state = self.ACTIVE
                    node_dict[n_pose[0]] = n_pose_node

            while prev_node_pair != None:
                prev_key = prev_node_pair[0]
                prev_link = prev_node_pair[1]
                prev_node = node_dict[prev_key]

                root_row = root_key//self.width
                root_column = root_key%self.width

                link_change = link2coor[(prev_link+4)%8]

                self.path_tree[root_row*3][root_column*3]=root_node.cost
                self.path_tree[root_row*3+link_change[0]][root_column*3+link_change[1]]=root_node.cost
                self.path_tree[root_row*3+link_change[0]*2][root_column*3+link_change[1]*2]=root_node.cost

                #mask[root_row][root_column]=1
                root_node.prev_node = None
                node_dict[root_key] = root_node

                root_key=prev_key
                root_node = node_dict[root_key]
                prev_node_pair = root_node.prev_node

        self.path_tree = np.expand_dims((self.path_tree/np.max(self.path_tree)*255).astype(np.uint8), axis=2)
        self.path_tree = np.concatenate([self.path_tree, self.path_tree, np.zeros((self.height*3, self.width*3,1), dtype=np.uint8)],axis=2 )
        #Image.fromarray((self.path_tree/np.max(self.path_tree)*255).astype(np.uint8)).save("./output/test_path_tree.png")
        Image.fromarray(self.path_tree).save("./output/test_path_tree.png")

    def get_path_from_tree(self, pose):
        path = []
        path.append(pose)
        pose = (pose[1],pose[0])
        pose_key = self.coordinate2key((pose[0]//3, pose[1]//3))
        while self.node_dict[pose_key].prev_node != None:
            new_pose_key = self.node_dict[pose_key].prev_node[0]
            prev_link = self.node_dict[pose_key].prev_node[1] 
            link_change = link2coor[prev_link]
            #new_pose_node = self.node_dict[new_pose_key]
            new_pose = self.key2coordinate(new_pose_key)
            path.append((new_pose[1]*3+link_change[1]*2,new_pose[0]*3+link_change[0]*2))
            path.append((new_pose[1]*3+link_change[1],new_pose[0]*3+link_change[0]))
            path.append((new_pose[1]*3,new_pose[0]*3))
            pose_key = new_pose_key
        return path

    def cost_map_generation(self):
        self.update_seed_node(self.seed)
        self.update_node_dict()
        self.pq = []
        heappush(self.pq, (0, self.coordinate2key(self.seed)))
        while len(self.pq)>0:
            prev_pop = heappop(self.pq)
            prev_node_key = prev_pop[1]
            prev_cost = prev_pop[0]

            prev_node_obj = self.node_dict[prev_node_key]
            if prev_node_obj.state == self.EXPAND:
                continue
            prev_node_obj.state = self.EXPAND
            self.node_dict[prev_node_key] = prev_node_obj
            for k, n_pose in enumerate(prev_node_obj.neighbours):
                n_pose_node = self.node_dict[n_pose[0]]
                n_pose_state = n_pose_node.state
                if n_pose_state==self.EXPAND:
                    continue
                elif n_pose_state==self.INITIAL:
                    new_cost = prev_cost+n_pose[1]
                    heappush(self.pq, (new_cost, n_pose[0]))
                    n_pose_node.state = self.ACTIVE
                    n_pose_node.cost = new_cost
                    n_pose_node.prev_node = (prev_node_key, k)
                    self.node_dict[n_pose[0]]=n_pose_node
                elif n_pose_state==self.ACTIVE:
                    new_cost = prev_cost+n_pose[1]
                    old_cost = self.node_dict[n_pose[0]].cost
                    if old_cost>new_cost:
                        heappush(self.pq, (new_cost, n_pose[0]))
                        n_pose_node.prev_node = (prev_node_key, k)
                        n_pose_node.cost = new_cost
                        self.node_dict[n_pose[-1]]=n_pose_node


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
                        PQ_Node(None,
                                self.INITIAL,
                                self.get_neighbor_node_keys((i,j),
                                    self.link_cost[i][j]),
                                0)
        self.margin_node_update()

    def update_seed(self, seed):
        self.seed = (seed[1], seed[0])

    def update_seed_node(self, seed):
        seed_key = self.coordinate2key(seed)
        seed_node = self.node_dict[seed_key]
        seed_node.prev_node = None
        self.node_dict[seed_key] = seed_node

    def update_node_dict(self):
        for key in self.node_dict:
            node_ = self.node_dict[key]
            node_.state = self.INITIAL
            self.node_dict[key]=node_
        self.margin_node_update()

    def margin_node_update(self):
        for i in [0, self.height-1]:
            for j in range(self.width):
                self.node_dict[self.coordinate2key((i,j))]=\
                        PQ_Node(None, self.EXPAND, None, 0)
        for i in range(self.height):
            for j in [0, self.width-1]:
                self.node_dict[self.coordinate2key((i,j))]=\
                        PQ_Node(None, self.EXPAND, None, 0)

    def update_path_dict(self, all_path):
        for path in all_path:
            for node in path:
                node_item = self.node_dict[self.coordinate2key((node[1],node[0]))]
                node_item.state = self.BORDER
                self.node_dict[self.coordinate2key((node[1],node[0]))]=node_item

    def generate_mask(self, path_point, close=True):
        mask = np.zeros((self.height, self.width),dtype=np.int32)
        dq = deque()
        inside_flag = False
        self.update_node_dict()
        self.update_path_dict(path_point)
        seed_row = np.random.randint(1, self.height-1)
        seed_column = np.random.randint(1, self.width-1)
        seed_key = self.coordinate2key((seed_row, seed_column))
        while self.node_dict[seed_key].state==self.BORDER:
            seed_row = np.random.randint(1, self.height-1)
            seed_column = np.random.randint(1, self.width-1)
            seed_key = self.coordinate2key((seed_row, seed_column))
        dq.append(seed_key)
        while len(dq) > 0:
            root_key = dq.popleft()
            root_node = self.node_dict[root_key]
            root_row = root_key//self.width
            root_column = root_key%self.width
            mask[root_row][root_column]=1
            self.node_dict[root_key] = root_node
            for n_pose in root_node.neighbours[::2]:
                n_pose_node = self.node_dict[n_pose[0]]
                n_pose_state = n_pose_node.state
                if n_pose_state == self.INITIAL:
                    dq.append(n_pose[0])
                    n_pose_node.state = self.ACTIVE
                    self.node_dict[n_pose[0]] = n_pose_node
                elif ((inside_flag == False) and (n_pose_state==self.EXPAND)):
                    inside_flag = True
        if inside_flag == True:
            mask[1:-1,1:-1] = 1-mask[1:-1,1:-1]
        self.contour_mask_list.append((mask[:], close))
        if close:
            self.mask = self.mask + mask
        return mask

    def delete_mask(self, idx_):
        if self.contour_mask_list[idx_][1]:
            self.mask = self.mask - self.contour_mask_list[idx_][0]
        del self.contour_mask_list[idx_]

    def coordinate_mask(self, x,y):
        for i, item in enumerate(self.contour_mask_list):
            if item[0][y][x] == 1:
                return i
        return -99

class PQ_Node():
    def __init__(self, prev_node, state, neighbours, cost):
        self.prev_node = prev_node
        self.state = state
        self.neighbours = neighbours
        self.cost = cost

if __name__=="__main__":
    import cv2
    #img = cv2.imread("../images/test2.jpg", cv2.IMREAD_GRAYSCALE)
    img = cv2.imread("./images/test3.jpeg")
    #img = cv2.resize(img, (15,15))
    seed = (240,199)
    obj = IntelligentScissor(img)
    #obj.link_calculation()
    #start = time.time()
    #obj.generate_all_node_dict()
    #print ("node dict time:", time.time()-start)
    obj.update_seed(seed)
    start = time.time()
    obj.cost_map_generation()
    print ("cost map time:", time.time()-start)
    obj.get_path((266,165))
