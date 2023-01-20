#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import csv
import os
import sys
from docplex.mp.progress import *
from docplex.mp.progress import SolutionRecorder
import docplex.mp.model as cpx
import time
import math
from absl import flags
FLAGS = flags.FLAGS


# In[1]:


class Solver:
    def __init__(self):
        pass
    def get_product(self,path):
        result = 1
        for edge in path:
            result = w_vars[l]*result
        return result
    
    def CPLEX_maximizing_QNU(self,wk_idx,network):
      
        opt_model = cpx.Model(name="QNUM")
        r_vars  = {(f,p): opt_model.continuous_var(lb=0, ub= network.max_edge_capacity,
                                  name="r_{0}_{1}".format(f,p))  for f in network.each_wk_flow_ids[wk_idx]
                                  for p in network.each_wk_flow_id_paths[wk_idx][f]}

        w_vars  = {(l): opt_model.continuous_var(lb=0, ub= 1,
                                  name="w_{0}".format(l))
                                  for l in network.set_E}
        def get_product(path,w_vars):
            result = 1
            for l in path:
                result = result*w_vars[l]
            return result
        #Edge constraint
        for edge_id,edge in network.set_E.items():
            opt_model.add_constraint(
                opt_model.sum(r_vars[f,p]
                for f in network.each_wk_flow_ids[wk_idx]
                for p in network.each_wk_flow_id_paths[wk_idx][f]
                if network.check_path_include_edge(edge_id,p))
                 <= network.each_edge_d_value[edge_id] *(1- w_vars[edge_id]), ctname="edge_capacity_{0}".format(edge_id))
                
        objective = opt_model.sum(math.log(r_vars[f,p]*(3*get_product(network.set_of_paths[p],w_vars)-1)) 
                            for f in network.each_wk_flow_ids[wk_idx]
                            for p in network.each_wk_flow_id_paths[wk_idx][f]
                              )


        # for maximization
        opt_model.maximize(objective)

    #     opt_model.solve()
        #opt_model.print_information()
        #try:
        opt_model.solve()


#         print('docplex.mp.solution',opt_model.solution)
        objective_value = -1
        try:
            if opt_model.solution:
                objective_value =opt_model.solution.get_objective_value()
        except ValueError:
            print(ValueError)
        return objective_value
    
    


# In[5]:





# In[ ]:




