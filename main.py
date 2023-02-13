#!/usr/bin/env python
# coding: utf-8

# In[1]:


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
from solver import PySCIP_solver
from solver import CPLEX_solver
from network import Network
import pdb
from os import listdir
from os.path import isfile, join
from threading import Thread


# In[ ]:


print("start ...")
# solver = CPLEX_solver()
solver = PySCIP_solver()
network = Network()
for backbone_link_lenght in [10,20,30,40,50,60]:
    network.set_d_value_of_edges(backbone_link_lenght)
    print("going to solve the QNUM optimization problem")
    utility = solver.maximizing_QNU(0,network)
    print("for backbone link lenght %s we have utility %s"%(backbone_link_lenght,utility))
    with open("results/results.csv", 'a') as newFile:                                
        newFileWriter = csv.writer(newFile)
        newFileWriter.writerow([backbone_link_lenght,utility])


# In[ ]:




