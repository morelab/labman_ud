# -*- coding: utf-8 -*-
"""
Created on Wed Jul 03 09:23:31 2013

@author: aitor
"""

import networkx as nx
import matplotlib.pylab as plt
from networkx.readwrite import json_graph
import json
import binascii
from networkx.readwrite import gexf

show_graphs = False

def load_graph(file_path, is_directed=False):
    if is_directed:
        G = nx.read_edgelist(path=file_path, delimiter=';', create_using= nx.DiGraph())
    else:
        G = nx.read_edgelist(path=file_path, delimiter=';')
    return G

def show_info(G):
    print 'Is directed?: %s' %(str(G.is_directed())) 
    print 'Nodes: %i' % (len(G.nodes()))
    print 'Edges: %i' % (len(G.edges()))
    
def export_json(file_path, G):
    data = json_graph.node_link_data(G)
    json.dump(data, open(file_path, 'w'))

def anonimize_json(input_file, output_file, G):
    f = open(input_file, 'r')
    file_text = f.read()
    f.close()
    for node in G.nodes():
        anon_name = str(binascii.crc32(node))
        file_text = file_text.replace(node, anon_name)
        
    f = open(output_file, 'w')
    f.write(file_text)
    f.flush()
    f.close()
    
def filter_pairs(G):
    if G.is_directed:
        filtered_G = nx.DiGraph()
        components = nx.weakly_connected_component_subgraphs(G)
    else:
        filtered_G = nx.Graph()
        components = nx.connected_component_subgraphs(G)
        
    for cc in components: 
        if len(cc.nodes()) > 2:
            filtered_G.add_nodes_from(cc)
            filtered_G.add_edges_from(cc.edges())  
    
    return filtered_G
    
    
def analyze_graph(G):    
    components = []    
    if not G.is_directed():
        components = nx.connected_component_subgraphs(G)
    else:
        components = nx.weakly_connected_component_subgraphs(G)
    
    i = 0
    
    for cc in components:            
        #Set the connected component for each group
        for node in cc:
            G.node[node]['component'] = i
        
        if show_graphs:
            nx.draw(cc)
            plt.show()
      
        #Calculate the in component betweeness, closeness and eigenvector centralities        
        cent_betweenness = nx.betweenness_centrality(cc)              
        cent_eigenvector = nx.eigenvector_centrality_numpy(cc)
        cent_closeness = nx.closeness_centrality(cc)
        
        for name in cc.nodes():
            G.node[name]['cc-betweenness'] = cent_betweenness[name]
            G.node[name]['cc-eigenvector'] = cent_eigenvector[name]
            G.node[name]['cc-closeness'] = cent_closeness[name]
        
        i +=1
               
    if not G.is_directed():
        # Calculate cliques
        cliques = list(nx.find_cliques(G))
        j = 0
        processed_members = []
        for clique in cliques:
            for member in clique:
                if not member in processed_members:
                    G.node[member]['cliques'] = []
                    processed_members.append(member)
                G.node[member]['cliques'].append(j)
            j +=1
        
        #calculate degree    
        degrees = G.degree()
        for name in degrees:
            G.node[name]['degree'] = degrees[name]
       
    else: #is_directed
        out_degrees = G.out_degree()
        in_degrees = G.in_degree()
        
        for name in G.nodes():
            G.node[name]['out_degree'] = out_degrees[name]
            G.node[name]['in_degree'] = in_degrees[name]
        
    betweenness = nx.betweenness_centrality(G)
    eigenvector = nx.eigenvector_centrality_numpy(G)
    closeness = nx.closeness_centrality(G)
    pagerank = nx.pagerank(G)
    
    for name in G.nodes():
        G.node[name]['betweenness'] = betweenness[name]
        G.node[name]['eigenvector'] = eigenvector[name]
        G.node[name]['closeness'] = closeness[name]
        G.node[name]['pagerank'] = pagerank[name]

        
    return G

#just for testing    
if __name__ == '__main__':
    print 'Loading graph'
    G = load_graph('./data/expertiseUndirected.csv', True)
    show_info(G)
    print 'filtering pairs'
    G = filter_pairs(G)
    show_info(G)
    G = analyze_graph(G)
    print G.nodes(data=True)
    export_json('./data/expertise-undirected.json', G)
    if G.is_directed():
        gexf.write_gexf(G, './data/expertise-undirected.gexf')
    print '************FIN*************'        