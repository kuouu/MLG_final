import networkx as nx
import numpy as np
from db import get_data, get_feature
import matplotlib as mpl
import matplotlib.pyplot as plt
import math
import pickle

def get_user_graph(
  start='2019-06-01', 
  end='2021-06-01'
):
  data = get_data(
    filter=['send_from', 'send_to', 'message'],
    start=start,
    end=end
  )
  features = get_feature()
  G = nx.DiGraph()

  # add edge by message
  for d in data:
    if G.has_edge(d[0], d[1]):
      G[d[0]][d[1]]['weight'] += len(d[2])
    else:
      G.add_edge(d[0], d[1], weight=len(d[2]))

  # remove node interaction < 10
  remove = []
  for u in G.nodes():
    weight_sum = np.array([G[u][v]['weight'] for v in G[u]]).sum()
    if weight_sum < 10:
      remove.append(u)
  G.remove_nodes_from(remove)
  remove = []
  for u in G.nodes():
    weight_sum = np.array([G[u][v]['weight'] for v in G[u]]).sum()
    if weight_sum <= 0:
      remove.append(u)
  G.remove_nodes_from(remove)

  # add node feature
  for node in G.nodes():
    index = np.where(features[:,0] == node)
    feature = np.squeeze(features[index], axis=0)
    G.nodes[node]['gender'] = feature[1]
    G.nodes[node]['feature'] = feature[2:]
  pickle.dump(G, open('./data/graph.pickle', 'wb'))
  return G

if __name__ == '__main__':
  G = get_user_graph(start='2021-5-15')
  print(nx.info(G))
  pos = nx.layout.spring_layout(G)

  node_sizes = [3 + 5 * G.degree[node] for node in G]
  node_colors = ["blue" if G.nodes[n]['gender'] == 'male' else 'red' for n in G.nodes]
  M = G.number_of_edges()
  edge_colors = range(2, M + 2)
  w = [G[edge[0]][edge[1]]['weight'] for edge in G.edges]
  edge_alphas = [(math.tanh(x)+1)/2 for x in w]

  nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors)
  edges = nx.draw_networkx_edges(
    G,
    pos,
    node_size=node_sizes,
    arrowstyle="->",
    arrowsize=10,
    edge_color=edge_colors,
    edge_cmap=plt.cm.Blues,
    width=2,
  )
  # set alpha value for each edge
  for i in range(M):
    edges[i].set_alpha(edge_alphas[i])

  pc = mpl.collections.PatchCollection(edges, cmap=plt.cm.Blues)
  pc.set_array(edge_colors)
  plt.colorbar(pc)

  ax = plt.gca()
  ax.set_axis_off()
  plt.show()