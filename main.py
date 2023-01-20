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
from network import Network
import pdb
from os import listdir
from os.path import isfile, join
from threading import Thread


# In[ ]:


solver = PySCIP_solver()
network = Network()
for backbone_link_lenght in [10,20,30,40,50,60]:
    network.set_d_value_of_edges(backbone_link_lenght)
    solver.maximizing_QNU(0,network)

