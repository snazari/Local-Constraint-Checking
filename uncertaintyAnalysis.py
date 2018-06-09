import numpy as np
from graph_tool.all import *
import pandas as pd
from tqdm import tqdm
import os
os.chdir('code')
from DirectedWeightedGraph import DWGraph
from config_helper import *
from run import run, run_config as v_elimination_demo
from config import Config
from information_content import demo as info_ratio_demo
from recursive_unique_tuples import *

os.chdir('/MAA/maa/waves/LCC_CC/graphtool/data/pnnl/')

print('Loading signal graphs')
filns        = ['G0S{}_pnnl_v3.edgelist'.format(i) for i in range(10)]
signalGraphs = [DWGraph.from_file_edge_list(filn,is_weighted=True,skip_first_line=False,make_undirected=False) for filn in filns]

print('Loading background graphs')
bfilns = ['G{}_pnnl_v3.edgelist'.format(i) for i in ['02','05','10','15','20']]
bGraphs= [DWGraph.from_file_edge_list(filn,is_weighted=True,skip_first_line=False,make_undirected=False) for filn in bfilns]

print('Finished loading all graphs')

print('Adding labels')
for g in signalGraph:
    g.add_default_labels()

for g in bGraphs:
    g.add_default_labels()

print('Done! Setting up data reduction parameters.')
eps = 1e-10
edges_matcher = EdgesMatcher(eps)
config = Config.get_config("default")
config.edges_matching_function = edges_matcher.e_matching
config.edges_typing = EdgesMatcher.edge_type
config.edges_epsilon_match = eps
config.lcc_max_iterations = 10
config.max_component_elements = 10

print('Starting DR experiment:')
for i in tqdm(bGraphs):
    for j in signalGraphs:
        print('Experiment: '+str(i)+'_'+str(j))
        t, t_new = DWGraph.vertex_elimination_r(i, j, 10, config.edges_matching_function)
        with open('t_'+str(i)+'_'+str(j), 'w') as f:
            # Print the subset we've got
            f.write(str(t))