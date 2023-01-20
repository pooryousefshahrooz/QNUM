#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import networkx as nx
from itertools import islice
import matplotlib.pyplot as plt
import random
from itertools import groupby
import time
import math as mt
import csv
import os
import random
from solver import Solver
import pdb
from os import listdir
from os.path import isfile, join
from threading import Thread


# In[2]:


class Network:
    def __init__(self):
        self.data_dir = './data/'
#         self.topology_file = self.data_dir+topology_file
#         self.topology_name = topology_file
#         self.toplogy_wk_scheme_result  = config.toplogy_wk_scheme_result_file
        c = 1
        etha = 10
        T = 10
        self.d =  (3*c*etha)/(2*T)
        self.each_wk_flow_ids = {}
        self.each_wk_flow_id_paths = {}

        self.each_edge_id = {}
        self.each_id_edge = {}
        self.set_of_paths = {}
        self.set_E = []
        self.max_edge_capacity = 230836
        self.each_edge_d_value ={}
        #self.load_topology(edge_capacity_bound)
        self.generate_workloads()
    def load_topology(self,each_edge_capacity_upper_bound):
        self.set_E=[]
        self.each_edge_capacity={}
        self.nodes = []
        self.each_edge_fidelity = {}
        self.link_idx_to_sd = {}
        self.link_sd_to_idx = {}
        self.g = nx.Graph()
        print('[*] Loading topology...', self.topology_file)
        try:
            f = open(self.topology_file+".txt", 'r')
        except:
            f = open(self.topology_file, 'r')
        header = f.readline()
        for line in f:
            line = line.strip()
            link = line.split('\t')
            #print(line,link)
            i, s, d,  c,l = link
            if int(s) not in self.nodes:
                self.nodes.append(int(s))
            if int(d) not in self.nodes:
                self.nodes.append(int(d))
            self.set_E.append((int(s),int(d)))
            self.max_edge_capacity = each_edge_capacity_upper_bound
            edge_capacity  = random.uniform(1,each_edge_capacity_upper_bound)
            edge_capacity = float(c)
            self.each_edge_distance[(int(s),int(d))] = float(l)
            self.each_edge_distance[(int(d),int(s))] = float(l)
            self.each_edge_capacity[(int(s),int(d))] = edge_capacity
            self.each_edge_capacity[(int(d),int(s))] = edge_capacity
            self.g.add_edge(int(s),int(d),capacity=edge_capacity,weight=1)
            self.g.add_edge(int(d),int(s),capacity=edge_capacity,weight=1)
        f.close()

        
    def generate_workloads(self):
        for i in range(1):
            self.each_wk_flow_ids[i]=[0,1,2,3,4]
        self.each_wk_flow_id_paths[0] = {}
        self.each_wk_flow_id_paths[0][0] = [0]
        self.each_wk_flow_id_paths[0][1] = [1]
        self.each_wk_flow_id_paths[0][2] = [2]
        self.each_wk_flow_id_paths[0][3] = [3]
        self.each_wk_flow_id_paths[0][4] = [4]
        self.set_E = {0:(0,5),1:(1,5),2:(2,5),3:(3,5),4:(4,5),5:(5,6),6:(6,7),7:(6,8),
                      8:(6,9),9:(6,10),10:(6,11)}
        self.each_edge_id = {(0,5):0,(1,5):1,(2,5):2,(3,5):3,(4,5):4,
                             (5,6):5,
                             (6,7):6,(6,8):7,(6,9):8,(6,10):9,(6,11):10
                            }
        self.each_id_edge = {0:(0,5),1:(1,5),2:(2,5),3:(3,5),4:(4,5),5:(5,6),
                            6:(6,7),7:(6,8),8:(6,9),9:(6,10),10:(6,11)}
        
        self.set_of_paths = {0:[0,5,6],1:[1,5,7],2:[2,5,8],3:[3,5,9],4:[4,5,10]
                            }
        
        self.each_edge_distance = {0:15,1:15,2:15,3:15,4:15,5:15,
                            6:15,7:15,8:15,9:15,10:15}
        
    def set_d_value_of_edges(self, backbone_link_lenght):
        c = 1
        for edge_id,edge in self.set_E.items():
            if edge ==(5,6):
                edge_length = backbone_link_lenght
            else:
                edge_length = self.each_edge_distance[edge_id]
            etha = 10**(-0.1*0.2*edge_length)
            T = (edge_length*10**(-4))/25# based on simulation setup of data link layer paper
            edge_d_value = (2*c*etha)/T
            self.each_edge_d_value[edge_id] = edge_d_value
            
        
    def get_fidelity(self,path_edges):
        if path_edges:
            F_product = (4*self.each_edge_fidelity[path_edges[0]]-1)/3 
            for edge in path_edges[1:]:
                F_product  = F_product*(4*self.each_edge_fidelity[edge]-1)/3
        else:
            print("Error")
            return 0.6
        N = len(path_edges)+1
        p1 = 1
        p2 = 1
        F_final = 1/4*(1+3*(p1*p2)**(N-1)*(F_product))
        return round(F_final,3)
    
   
    def get_edges(self):
        return self.set_E

    def check_path_include_edge(self,edge,path):
        print("checking edge %s in path %s"%(edge,path))
        if self.set_E[edge] in self.set_of_paths[path] or (self.set_E[edge][1],self.set_E[edge][0]) in self.set_of_paths[path]:
            return True
        else:
            return False
        
    def get_flows_using_this_edge(self,wk_idx,edge):
        flow_list = []
        for flow in self.each_wk_flow_ids[wk_idx]:
            for path in self.each_wk_flow_id_paths[wk_idx][f]:
                if self.check_path_include_edge(edge,path):
                    flow_list.append(flow)
        return flow_list
        
    def get_path_length(self,path):
        return self.each_path_legth[path]-1

    



# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




