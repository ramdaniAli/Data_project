import random
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import math
from pymongo import MongoClient
import pprint
import datetime

rnd = np.random  # random helper
rnd.seed(0)

clients_count = 5  # random.randrange(3, 10)  # nombre de clients hamiltonien  >= 3

min_d = math.ceil(clients_count / 2)  # degre min required
max_d = clients_count - 1  # degre max required

xc = rnd.rand(clients_count + 1) * 200  # random number in list (positions gps)
yc = rnd.rand(clients_count + 1) * 100

nodes_list = [i for i in range(clients_count)]  # liste de sommets clients + depot

# nodes_positions = {i: {"lat": xc[i], "long": yc[i]} for i in nodes_list} # position lat , long de chaque point

# list of eges , (hamiltonien)
A_hamiltonien = []

G = nx.Graph()  # graph init


def deg(s):
    deg = 0
    for n in A_hamiltonien:
        if (n[0] == s or n[1] == s):
            deg = deg + 1
    return deg


def arr(s1, s2):
    for i in A_hamiltonien:
        if (i[0] == s2 and i[1] == s1):
            return True
    return False


for i in nodes_list:
    deg_rand = random.randrange(min_d, max_d + 1)
    deg_actu = deg(i)
    while (deg_actu < deg_rand):
        sommet = random.randrange(0, len(nodes_list))
        if (sommet != i):
            if (deg(sommet) < max_d and not arr(i, sommet) and not arr(sommet, i)):
                deg_actu = deg_actu + 1
                A_hamiltonien.append((i, sommet))
                arr(i, sommet)

A_mutation_hamiltonien = [
    (str(i), str(j), {'weight': round(np.hypot(xc[i] - xc[j], yc[i] - yc[j]), 2), 'trafic': random.choice(['f', 'd'])})
    for i, j in A_hamiltonien
]  # matrice hamiltonienne

G.add_edges_from(A_mutation_hamiltonien)  # arcs init

# splitting edges
elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > 50]
esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] <= 50]
dense = [(u, v) for (u, v, d) in G.edges(data=True) if d["trafic"] == "d"]
fluid = [(u, v) for (u, v, d) in G.edges(data=True) if d["trafic"] == "f"]

pos = nx.spring_layout(G)  # positionement des sommets

plt.figure(figsize=(15, 8))
plt.title('Graph complet avec ditances et trafic ')

# nodes
nx.draw_networkx_nodes(G, pos, node_size=800)

# edges
nx.draw_networkx_edges(
    G, pos, edgelist=elarge, width=3, alpha=1, edge_color="orange"
)

nx.draw_networkx_edges(
    G, pos, edgelist=esmall, width=3, alpha=1, edge_color="blue"
)
nx.draw_networkx_edges(
    G, pos, edgelist=dense, width=2, alpha=1, edge_color="red", style="dashed"
)
nx.draw_networkx_edges(
    G, pos, edgelist=fluid, width=2, alpha=1, edge_color="green", style="dashed"
)

# get attributes
edge_labels_w = nx.get_edge_attributes(G, 'weight')
edge_labels_t = nx.get_edge_attributes(G, 'trafic')

# labels
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels_w, font_size=12)
# nx.draw_networkx_edge_labels(G , pos , edge_labels=edge_labels_t  ,font_size=12 )

nx.draw_networkx_labels(G, pos, font_size=20, font_family="sans-serif")

plt.axis("off")
plt.show()

# créer le client qui va se connecter à la base de données et récupérer la collection véhicules
client = MongoClient("mongodb+srv://dataUser:ORACLE@clusterdataproject.pow6j.mongodb.net/test")
db = client['db_data_project']
collection_node_positions = db['nodes_position']
collection_edges = db['edges']

mutate_eges = [

    {
        "node1": i,
        "node2": j,
        "distance": round(np.hypot(xc[i] - xc[j], yc[i] - yc[j]), 2),
        "trafic": random.choice(['f', 'd'])
    }

    for i, j in A_hamiltonien
]  # mutate edges to collection mongo db


mutate_node_position = [
    {'node': i, "lat": xc[i], "long": yc[i]}
    for i in nodes_list
]  # mutate position to collection mongo db

collection_edges.drop()
collection_node_positions.drop()

#ajouter plusieurs document a la fois
collection_edges.insert_many(mutate_eges)
collection_node_positions.insert_many(mutate_node_position)

