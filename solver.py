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


class PySCIP_solver:
    def maximizing_QNU(self,wk_idx):
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
            model.addCons(sum(w[t,k,p] * (2/each_path_purification_succ_probability[p])   
            for f in network.each_wk_flow_ids[wk_idx] for p in network.each_wk_flow_id_paths[wk_idx][f] 
                              if network.check_path_include_edge(edge_id,p)) <= network.each_edge_d_value[edge_id] *(1- w_vars[edge_id]), "edge_capacity_{%s}" % edge_id)

        # new constraint
        model.addCons(z <= sum(math.log(r_vars[f,p]*(3*get_product(network.set_of_paths[p],w_vars)-1)) 
                            for f in network.each_wk_flow_ids[wk_idx]
                            for p in network.each_wk_flow_id_paths[wk_idx][f])  , "Objective_constaint(z)")


        # Objective
        model.setObjective(z , "maximize")

    #     model.data = x
        model.optimize()
        print("Optimal value:",model.getObjVal())


# In[ ]:




