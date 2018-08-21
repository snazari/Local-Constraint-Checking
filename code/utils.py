import numpy as np
import pandas as pd
from collections import Counter
from graph_tool.all import *
from information_content import *

class utilities:
    def compute_snr(signal,noise):
        return 10*np.log10(signal.Attribute.var()/noise.Attribute.var())
    
    def makeEdgelist(filename,writename,u='Source',v='Destination',w='Weight'):
        dG = pd.read_csv(filename,usecols=[u,v,w])
        np.savetxt(writename,dG[[u,v]].values,fmt='%i %i')
        return dG
    
    def makeDWGraph(filename,atts,serialize):
        g = DWGraph.from_file_edge_list(filename,is_weighted=False,skip_first_line=False,make_undirected=False)
        g.add_labels_from_file(atts)
        if serialize==True:
            pickle.dump(g,open(filename+'_graph.p','wb'))
        return g
    
    def reduceGraph(g,g0,N,config):
        t, t_new = DWGraph.vertex_elimination_r(g, g0, N, config.edges_matching_function)
        return t, t_new
    
    def getSubgraphs(g,g0,t_new):
        vertices_list_old_to_old, vertices_list_new_to_old = \
        DWGraph.get_vertices_list_recursive(g, g0, t_new,output_file=None,
                                            edges_matching=config.edges_matching_function,comp_approx=60)
        # Get list of subgraphs
        g_subgraphs = DWGraph.get_graphs_by_vertices_list(g0, vertices_list_new_to_old)
        return g_subgraphs
    
    def createNodeAttributes(filename,save):
        dS = pd.read_csv(filename,usecols=['FromNode','SourceLatitude'])
        dD = pd.read_csv(filename,usecols=['ToNode','DestinationLatitude'])
        dS.columns = ['Node','Attribute']
        dD.columns = ['Node','Attribute']
        df = dS.append(dD)
        df.drop_duplicates(subset=['Node'],inplace=True)
        if save == True:
            np.savetxt(str(filename)+'.attr',df.values,fmt='%i %.15f')
        return df
    
    def getNodes(filename):
        df = pd.read_csv(filename,usecols=['FromNode','ToNode'])
        return set(df.FromNode.values).union(df.ToNode.values)
    
    def signalAttr(nodelist,channel,signal,save):
        b = list(nodelist)
        atts=createNodeAttributes(channel,save=False)
        dfs=atts.loc[atts['Merged'].isin(b)]
        if save == True:
            np.savetxt(str(signal)+'.attr',dfs.values,fmt='%i %i')
        return dfs
    #return atts
    #dfs=graph_att.loc[graph_att['Merged'].isin(b)];dfs
    def check_symmetric(a, tol=1e-8): # check if a matrix is symmetric
        return np.allclose(a, a.T, atol=tol)
    
    def get_unique_nodes_from_df(df,u,v):
        return len(set(df.u.values).union(set(df.v.values)))
                         
    def count_edges_uv(G):
        '''
        This method accepts a DWGraph object and returns a pandas dataframe with columns (u,v,w)
        where w is the number of edges between the endnodes (u,v). 
        In other words, this method counts the number of multi-edges for an edge in G.
        '''
        #Gc = G.copy()
        g_edges=G.get_edges()
        u = g_edges[:,0]
        v = g_edges[:,1]
        tp= zip(u,v)
        cnt=Counter(tp)
        m = list(cnt.keys())
        df= pd.DataFrame(m,columns=['u','v'])
        df['w'] = pd.Series(list(cnt.values()))
        return df