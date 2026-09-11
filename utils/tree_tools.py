import networkx as nx
import streamlit as st
import pandas as pd

def root(graph):
    """
    Returns the root of a tree
    
    Parameters
    ----------
    graph : nx.DiGrap()
        tree (directed acyclic graph)

    Returns
    -------
    n : node object
        label of the root of graph

    """
    for n in graph.nodes():
        if graph.in_degree(n) == 0:
            return n

def load_from_OpenStemmata(file):
    '''
    returns a nx.DiGraph() tree from database .dot files
    '''
    G = nx.nx_pydot.read_dot(file)
    # remove uncertain paternity
    edges_pt = nx.get_edge_attributes(G, 'style')
    for edge, pt in edges_pt.items():
        if pt =='dashed':
            G.remove_edge(*edge)
    
    # remvove singletons and extra-stemmatic contaminations
    singletons = []
    for node in G.nodes():
        if G.in_degree(node) == 0 and G.out_degree(node) == 0:
            singletons.append(node)
    G.remove_nodes_from(singletons)
    
    # identify surviving witnesses
    colors = nx.get_node_attributes(G, 'color')
    living = {}
    for node in G.nodes():
        if node in colors.keys():
            living[node] = False
        else:
            living[node] = True
    nx.set_node_attributes(G, living, 'witness')
    
    return G

def degree(G, n):
    """
    wrapper of nx.DiGraph().out_degree()
    """
    return G.out_degree(n)

def witness_nb(g):
    return sum([g.nodes[n]['witness'] for n in g.nodes()])

