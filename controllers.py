#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from threading import Thread
import threading
import logging
import time
import queue
import random
import csv


# In[ ]:





# In[ ]:


class Node_controller:
    def __init__(self,node_id,attached_links):
        print("we are in node controller for node %s "%(node_id))
        self.lock = threading.Lock()
        self.node_id = node_id
        self.attached_links = attached_links
        global each_node_link_buffer_congestion_flag
        self.main()
        
    def getCombinations(self,seq):
        combinations = list()
        for i in range(0,len(seq)):
            for j in range(i+1,len(seq)):
                combinations.append([seq[i],seq[j]])
        return combinations

    def check_source_end(self,flow_id):
        global each_flow_source_end
        if each_flow_source_end[flow_id]==self.node_id:
            return True
        else:
            return False
    def consume_EPR_pair(self,flow_id):
        """we can simulate the teloprtation here
        or we can simulate the overflow on a source node when the rate of teleporting qubits is higher than 
        the rate the network generates ent-to-end EPR pairs"""
        pass
    def add_item(self,key1,key2,key3,list_of_values,new_buffer):
        try:
            new_buffer[key1][key2][key3] = list_of_values
        except:
            try:
                new_buffer[key1][key2]={}
                new_buffer[key1][key2][key3] = list_of_values
            except:
                try:
                    new_buffer[key1]={}
                    new_buffer[key1][key2]={}
                    new_buffer[key1][key2][key3] = list_of_values
                except ValueError:
                    print("ValueError ",ValueError)
        return new_buffer
    
    def swap(self):
        """this function for each flow, swaps the stored EPR pairs in memory"""
        #print("we are in swap function ")
        global buffer
        global each_link_nodes
        #print("we are going to swap on buffer %s "%(buffer))
        if len(self.attached_links)>1:
            self.lock.acquire()
            new_buffer = {}
            
            for link_pair in self.getCombinations(self.attached_links):
                left_link  = link_pair[0]
                right_link = link_pair[1]
#                 print("left %s and right %s are links for node %s "%(left_link,right_link,self.node_id))
                for flow1,EPR_left_link_time_slots in buffer[self.node_id][left_link].items():
                    # if this node is the source node, consume the EPR pair but if the end-to-end has established
                    if self.check_source_end(flow1):
                        self.consume_EPR_pair(flow1)
                    else:
                        for flow2,EPR_right_link_time_slots in buffer[self.node_id][right_link].items():
                            if flow1==flow2:#this means flow on left and right links are same
                                if self.node_id==1:
                                    print("node %s for flow %s left %s right %s EPRs"%(self.node_id,flow1,len(EPR_left_link_time_slots),len(EPR_right_link_time_slots)))
            
            
            
            for link_pair in self.getCombinations(self.attached_links):
                left_link  = link_pair[0]
                right_link = link_pair[1]
#                 print("left %s and right %s are links for node %s "%(left_link,right_link,self.node_id))
                for flow1,EPR_left_link_time_slots in buffer[self.node_id][left_link].items():
                    # if this node is the source node, consume the EPR pair but if the end-to-end has established
                    if self.check_source_end(flow1):
                        self.consume_EPR_pair(flow1)
                    else:
                        for flow2,EPR_right_link_time_slots in buffer[self.node_id][right_link].items():
                            if flow1==flow2:#this means flow on left and right links are same

                                # we swap and which link (left or right) that has higher EPR pairs will have some left
                                left_epr_time_slots = []
                                for i in range(min(len(EPR_left_link_time_slots),len(EPR_right_link_time_slots)),max(len(EPR_left_link_time_slots),len(EPR_right_link_time_slots))):
                                    if len(EPR_left_link_time_slots)< len(EPR_right_link_time_slots):
                                        left_epr_time_slots.append(EPR_right_link_time_slots[i])
                                    else:
                                        left_epr_time_slots.append(EPR_left_link_time_slots[i])
                                if self.node_id== each_link_nodes[left_link][0]:
                                    left_node = each_link_nodes[left_link][1]
                                    right_node = each_link_nodes[right_link][0]
                                else:
                                    left_node = each_link_nodes[left_link][0]
                                    right_node = each_link_nodes[right_link][1]


                                if len(EPR_left_link_time_slots)< len(EPR_right_link_time_slots):
                                    new_buffer = self.add_item(self.node_id,left_link,flow1,[],new_buffer)
                                    new_buffer = self.add_item(self.node_id,right_link,flow1,left_epr_time_slots,new_buffer)

                                    new_buffer = self.add_item(left_node,left_link,flow1,[],new_buffer)
                                    new_buffer = self.add_item(right_node,right_link,flow1,left_epr_time_slots,new_buffer)

                                else:
                                    new_buffer = self.add_item(self.node_id,right_link,flow1, [],new_buffer)
                                    new_buffer = self.add_item(self.node_id,left_link,flow1,left_epr_time_slots,new_buffer)

                                    new_buffer = self.add_item(left_node,left_link,flow1, [],new_buffer)
                                    new_buffer = self.add_item(right_node,right_link,flow1,left_epr_time_slots,new_buffer)


            for node,link_flow_EPRts in new_buffer.items():
                for link,flow_EPRts in link_flow_EPRts.items():
                    for flow, EPRts in flow_EPRts.items():
                        buffer[node][link][flow] = EPRts
            self.lock.release()
        
    def send_congestion_signal(self,link_id):
        """when there is buffer overflow, we send a congestion signal"""
        print("The buffer overflow happended, we send a congestion signal!")
        global each_node_link_buffer_congestion_flag
        each_node_link_buffer_congestion_flag[self.node_id][link_id] =True
    def node_congestion(self):
        """this function checks if there is any overflow in buffer"""
        global buffer
        global each_node_each_link_capacity        
        for link,flow_EPR_ts in buffer[self.node_id].items():
            Aggregate_EPRs = 0
            for flow1,EPRs_ts in flow_EPR_ts.items():
                Aggregate_EPRs =Aggregate_EPRs+len(EPRs_ts) 
            if Aggregate_EPRs >= each_node_each_link_capacity[self.node_id][link]:
                if self.node_id==1:
                    print("node %s aggregate EPR on link %s are %s higher than capacity %s "%(self.node_id,link,Aggregate_EPRs,each_node_each_link_capacity[self.node_id][link]))
                return True,link
        return False,0
    def main(self):
        """this is the main function of repeater or node controller
        it continiously in a discrite time manner, swaps EPR pairs and check for congestion"""
        global buffer
        global each_flow_source_end
        while(True):
            self.swap()
            congestion_flag,link_id = self.node_congestion()
            if congestion_flag:
#                 print("buffer over flow on node %s on buffer for link %s "%(self.node_id,link_id))
                self.send_congestion_signal(link_id)
            else:
                time.sleep(1)
                


# In[ ]:





# In[ ]:


class Link_controller:
    def __init__(self,link_id,attached_flows,link_success_prob,link_propagation_delay):
        print("we are in link controller for %s "%(link_id))
        self.link_id = link_id
        self.link_success_prob = link_success_prob
        
        # this is the rate that the link can generate EPR pairs which can be a function of the link length
        self.link_rate = each_link_rate[link_id]
        
        # we use this to control the time that is required to accomplish one attempt for EPR pair generation
        # this can be computed from Prajit's paper
        self.link_propagation_delay = link_propagation_delay
        # this controls after how many attempt tp generate EPR pairs we will update the rates
        global learning_step_value
        self.learning_step = learning_step_value
        
        self.epr_link_generation_counter = 0
        self.time_slot_counter = 0
        # this will be used in rate normalization
        self.sum_rates = 0
        # we use this flag to check if the rates has converged and we do not need to update the rates
        self.convergence_flag = False
        # by default the buffer overflow flag from two nodes of the link is False
        self.buffer_congestion_signal = False
        
        self.each_flow_rate = {}
        self.each_flow_normalized_rate ={}
        for flow in attached_flows:
            self.each_flow_rate[flow]= 1
        self.normalized_rates()
        self.lock = threading.Lock()
        
        
        self.link_attempt_duration = link_propagation_delay
        #we use this queue to track when an attempt will finish
        self.q = queue.Queue()
        self.q.put(link_propagation_delay)
        
        
        
        self.main()
    def normalized_rates(self):
        global max_link_capacity
        for flow,rate in self.each_flow_rate.items():
            self.sum_rates = self.sum_rates+rate
        for flow,rate in self.each_flow_rate.items():
            # we divide by the maximum link capacity in the network to implement different rates at two sides
            self.each_flow_normalized_rate[flow] = rate/max_link_capacity
    def update_rates(self,flow_id):
        """ in this function, the link controller updates its rates. 
        It could get the rates from a centralized controller 
        or it can compute from a set of rules """
        #print("we are going to update the rates")
        global max_link_capacity
        self.lock.acquire()
        new_flow_rate = {}
        if not self.congestion_flag:
            print(" ************ no congestion and increase by one the rate of flow %s "%(flow_id))
            for flow,rate in self.each_flow_rate.items():
                if flow_id ==flow:
                    new_rate = rate+1
                else:
                    new_rate = rate
                new_flow_rate[flow] = new_rate
        else:
            print(" ************* congestion has accured and divide the rate of flow %s by 2 "%(flow_id))
            for flow,rate in self.each_flow_rate.items():
                if flow_id ==flow:
                    new_rate = rate/2
                else:
                    new_rate = rate
                new_flow_rate[flow] = new_rate
            self.congestion_flag = False
        self.each_flow_rate = new_flow_rate
        self.lock.release()
        self.normalized_rates()
    def attempt_to_generate_epr_pair(self):
        """this function each time tries to generate one EPR pairs and 
        assings the generated link (if any) to a flow based on the rate of flow"""
        random_value = random.uniform(0,1)
        attemp_success_time_slot  = self.link_attempt_duration+self.time_slot_counter
        self.q.put(attemp_success_time_slot)
#         print("we added one attempt to the queue")
        
        # we save the rates of flows at each link controller at each step
        global flow_rate_on_each_link_controller_tracking_file_path
        self.lock.acquire()
        for flow,rate in self.each_flow_rate.items():
            with open(flow_rate_on_each_link_controller_tracking_file_path, 'a') as newFile:                                
                newFileWriter = csv.writer(newFile)
                newFileWriter.writerow([self.link_id,flow,rate,attemp_success_time_slot])
        self.lock.release()
           
    def check_arrived_buffer_congestion_signal(self):
        """this function checks if the aggregate rates of flows on this link is above its capacity
        it first check if the congestion flag is set by node controller for buffer overflow"""
        global each_node_link_buffer_congestion_flag
        global each_link_nodes
        if each_node_link_buffer_congestion_flag[each_link_nodes[self.link_id][0]][self.link_id] or each_node_link_buffer_congestion_flag[each_link_nodes[self.link_id][1]][self.link_id]:
            self.congestion_flag = True
            if each_node_link_buffer_congestion_flag[each_link_nodes[self.link_id][0]][self.link_id]:
                print("**** there is congestion signal received from node %s buffer overflow "%(each_node_link_buffer_congestion_flag[each_link_nodes[self.link_id][0]][self.link_id]))
            else:
                print("**** there is congestion signal received from node %s buffer overflow "%(each_node_link_buffer_congestion_flag[each_link_nodes[self.link_id][1]][self.link_id]))
        else:
            self.congestion_flag = True
                        
    def check_congestion(self):
        """this function checks if the aggregate rates of flows on this link is above its capacity
        it first check if the congestion flag is set by node controller for buffer overflow"""
        global each_node_link_buffer_congestion_flag
        global each_link_nodes
        aggregate_rate = 0
        for flow,rate in self.each_flow_rate.items():
            aggregate_rate = aggregate_rate+rate
        if aggregate_rate>self.link_rate:
            self.congestion_flag = True
            print(" *** there is link capacity congestion on link %s "%(self.link_id))
        else:
            self.congestion_flag = False
            #print("there is no congestion! aggregate_rate %s "%(aggregate_rate))
    def attempt_result(self):
        if not self.q.empty():
            if self.time_slot_counter>=self.q.queue[0]:
                return True
            else:
                return False
        else:
            return False
        
    def assign_flow(self,random_value):
        self.lock.acquire()
        sorted_normalized_rates = []
        for flow,normalized_rate in self.each_flow_normalized_rate.items():
            sorted_normalized_rates.append(normalized_rate)
        sorted_normalized_rates.sort()
        random_value =random.uniform(0,1) 
        for normalized_rate in sorted_normalized_rates:
            if random_value< normalized_rate:
                for flow,normal_rate in self.each_flow_normalized_rate.items():
                    if normal_rate==normalized_rate:
                        self.lock.release()
                        #print("we are assigning the EPR to flow %s "%(flow))
                        return flow
        self.lock.release()
        flow_id = list(self.each_flow_rate)[random.randint(0,len(self.each_flow_rate)-1)]
        #print("we randomly selected this flow %s and we will assign EPR to it "%(flow_id))
        return flow_id
    def update_buffer(self,flow_id):
        global buffer
        global each_link_nodes
        self.lock.acquire()
#         print("buffer ",buffer)
#         for node,link_flow_EPRs in buffer.items():
#             for link,flow_EPRs in link_flow_EPRs.items():
#                 for flow,EPRs in flow_EPRs.items():
#                     print("for node %s on link %s flow %s EPRs %s "%(node,link,flow,EPRs))
#         print("each_link_nodes[self.link_id] for %s is %s "%(self.link_id, each_link_nodes[self.link_id]))
#         print("we update the buffer on node %s link %s flow %s "%(self.link_id,each_link_nodes[self.link_id][0],flow_id))
#         print("we update the buffer on node %s link %s flow %s "%(self.link_id,each_link_nodes[self.link_id][1],flow_id))
        
        buffer[each_link_nodes[self.link_id][0]][self.link_id][flow_id].append(self.time_slot_counter)
        buffer[each_link_nodes[self.link_id][1]][self.link_id][flow_id].append(self.time_slot_counter)
        self.lock.release()
    def main(self):
        """in this function, the link controller continiously update its rates and 
        generate EPR pairs based on them. 
        """
        while(True):
            if self.attempt_result():
                self.q.get()
                random_value = random.uniform(0,1)
                flow_id = self.assign_flow(random_value)
                self.check_arrived_buffer_congestion_signal()
                if self.congestion_flag:
                    print("link %s has received a buffer overflow congestion from one of the nodes"%(self.link_id))
                    self.update_rates(flow_id)
                if random_value<= self.link_success_prob:
                    self.update_buffer(flow_id)
                    if (self.epr_link_generation_counter%self.learning_step)==0:
                        #print("************** we are going to updat the rate!")
                        self.check_congestion()
                        self.update_rates(flow_id)
                    #else:
                        #print(" ************* not updating yet %s / %s %s  "%(self.epr_link_generation_counter,self.learning_step,self.epr_link_generation_counter%self.learning_step))
                    self.epr_link_generation_counter+=1
                
            self.attempt_to_generate_epr_pair()
            self.time_slot_counter+=1
            time.sleep(2)
                    


# In[ ]:





# In[ ]:


def worker(flag,edge_node_id,attached_flows_links,each_edge_success_probability,each_link_propagation):
    if flag:
        link_controller = Link_controller(edge_node_id,attached_flows_links,each_edge_success_probability,each_link_propagation)
    else:
        node_controller  =Node_controller(edge_node_id,attached_flows_links)

def global_controller():
    each_edge_success_probability = {}
    for edge in edges:
        random_link_success_p = random.uniform(0.2,0.9)
        if edge==1:
            random_link_success_p=1
        else:
            random_link_success_p=0.1
        each_edge_success_probability[edge] = random_link_success_p
    for edge in edges:
        attached_flows = each_link_flows[edge]
        t = threading.Thread(target=worker, args=(True,edge,attached_flows,each_edge_success_probability[edge],each_link_propagation[edge],))
        t.setDaemon(True)
        t.start()
        
            
    for node in nodes:
        t2 = threading.Thread(target=worker, args=(False,node,each_node_attached_links[node],None,None,))
        t2.setDaemon(True)
        t2.start()
    logging.debug('Waiting for worker threads')
    main_thread = threading.currentThread()
    for t in threading.enumerate():
        if t is not main_thread:
            t.join()


# In[ ]:


learning_step_value =5
flow_rate_on_each_link_controller_tracking_file_path = "results/flow_rate_on_each_link_controller_tracking_file_path.csv"
edges = [0,1,2,3]
nodes = [0,1,2,3,4]
max_link_capacity = 20
each_link_rate = {0:100,1:100,2:100,3:100}
each_link_nodes = {0:[0,1],1:[1,2],2:[2,3],3:[3,4]}
each_link_propagation = {0:4,1:4,2:6,3:4}
each_node_attached_links = {
    0:[0],
    1:[0,1],
    2:[1,2],
    3:[2,3],
    4:[3]}
flows = [0]
each_link_flows = {0:[0],1:[0],2:[0],3:[0]}
each_link_nodes ={0:[0,1],1:[1,2],2:[2,3],3:[3,4]}
buffer = {#each_node_id_link_id_each_attached_flow_id_ts_of_generated_EPRs
    0:{0:{0:[0]}},
    1:{0:{0:[0]},1:{0:[0]}},
    2:{1:{0:[0]},2:{0:[0]}},
    3:{2:{0:[0]},3:{0:[0]}},
    4:{3:{0:[0]}}}

each_flow_source_end ={0:[0,4]}
each_node_each_link_capacity = {
    0:{0:100},
    1:{0:100,1:100},
    2:{1:100,2:100},
    3:{2:100,3:100},
    4:{3:100}}
each_node_link_buffer_congestion_flag = {0:{0:False},1:{0:False,1:False},2:{1:False,2:False},
                                         3:{2:False,3:False},4:{3:False}}
# node_controller  =Node_controller(1,each_node_attached_links[1])
# link_controller = Link_controller(1,each_link_flows[1],0.8,each_link_propagation[1])
global_controller()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




