#!/usr/bin/env python
# coding: utf-8

# In[2]:


import csv
import os
import sys
from docplex.mp.progress import *
from docplex.mp.progress import SolutionRecorder
import docplex.mp.model as cpx
from math import log
import time
import math
from pyscipopt import Model, quicksum, multidict


# In[1]:


class CPLEX_solver:
    def __init__(self):
        pass
    def get_product(self,path):
        result = 1
        for edge in path:
            result = w_vars[l]*result
        return result
    
    def maximizing_QNU(self,wk_idx,network):
      
        opt_model = cpx.Model(name="QNUM")
        r_vars  = {(f,p): opt_model.continuous_var(lb=0, ub= network.max_edge_capacity,
                                  name="r_{0}_{1}".format(f,p))  for f in network.each_wk_flow_ids[wk_idx]
                                  for p in network.each_wk_flow_id_paths[wk_idx][f]}

        w_vars  = {(l): opt_model.continuous_var(lb=0, ub= 1,
                                  name="w_{0}".format(l))
                                  for l in network.set_E}
        
        z_vars  = {opt_model.continuous_var(lb=0, ub= 1000,
                                  name="z")
                                  }
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
                 <= network.each_edge_d_value[edge_id] *(1- w_vars[edge_id]),
                ctname="edge_capacity_{0}".format(edge_id))
            
            
#         opt_model.add_constraint(
#                 opt_model.sum(math.log(r_vars[f,p]*(3*get_product(network.set_of_paths[p],w_vars)-1)) 
#                             for f in network.each_wk_flow_ids[wk_idx]
#                             for p in network.each_wk_flow_id_paths[wk_idx][f])>=z_vars,
#                               ctname="objective")

#         objective = opt_model.sum(z_vars)
        
        
#         objective = opt_model.sum(math.log(r_vars[f,p]*(3*get_product(network.set_of_paths[p],w_vars)-1)) 
#                             for f in network.each_wk_flow_ids[wk_idx]
#                             for p in network.each_wk_flow_id_paths[wk_idx][f]
#                               )

        objective = opt_model.sum(log(r_vars[0,0]*(3*w_vars[0]-1))+log(r_vars[1,0]*(3*w_vars[0]-1)))
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
    
    


# In[1]:


class PySCIP_solver:
    def __init__(self):
        pass
    def maximizing_QNU(self,wk_idx,network):
        """mctransp -- model for maximizing quantum network utility maximization Problem
        Parameters:
        - r_vars[]: rates of paths/routes

        - w_vars: link variable that controls the capacity and fidelity
       
        Returns the objective value.
        """

        model = Model("quantum network utility maximization")
        def get_product(path,w_vars):
            result = 1
            for l in path:
                result = result*w_vars[l]
            return result
        # Create variables
        r_vars = {}
        w_vars = {}
        

  
        for f in network.each_wk_flow_ids[wk_idx]:
            for p in network.each_wk_flow_id_paths[wk_idx][f]:
                r_vars[f,p] = model.addVar(vtype="C",lb=0,ub=network.max_edge_capacity, name="r(%s,%s)" % (f,p))

        for l in network.set_E:
            w_vars[l] = model.addVar(vtype="C",lb=0,ub=1,name="w(%s)" % (l))

        z = model.addVar(vtype="C", name="z")

        # edge Capacity constraints
        for edge_id,edge in network.set_E.items():
            model.addCons(sum(r_vars[f,p] for f in network.each_wk_flow_ids[wk_idx] 
                              for p in network.each_wk_flow_id_paths[wk_idx][f] 
                              if network.check_path_include_edge(edge_id,p)) <= network.each_edge_d_value[edge_id] *(1- w_vars[edge_id]), "edge_capacity_{%s}" % edge_id)

        # new constraint
        model.addCons(z <= sum(log(r_vars[0,0]*((3*w_vars[0])-1))+ log(r_vars[1,0]*((3*w_vars[0])-1))) , "Objective_constaint(z)")



        # Objective
        model.setObjective(z , "maximize",method="Nelder-Mead")

    #     model.data = x
        model.optimize()
        #print("Optimal value:",model.getObjVal())
        
        for f in network.each_wk_flow_ids[wk_idx]:
            for p in network.each_wk_flow_id_paths[wk_idx][f]:
                flag =  network.check_path_include_edge(5,p)
                print("for flow %s and p %s we have r_%s_%s %s and backbone capacity %s flag of using the edge %s"%(f,p,f,p,model.getVal(r_vars[f,p]),network.each_edge_d_value[5] *(1- model.getVal(w_vars[5])),flag))
        for l in network.set_E:
            print("for edge %s we have w_wars_%s %s"%(l,l,model.getVal(w_vars[l])))
        return model.getObjVal()


# In[ ]:





# In[ ]:




