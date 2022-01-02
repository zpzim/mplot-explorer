import numpy as np
import copy

class GraphNode:
  def __init__(self, seq):
    self.start = seq
    self.end = seq

  def __init__(self, start, end):
    self.start = start
    self.end = end

  def __str__(self):
    return 'Start: {}, End: {}'.format(self.start, self.end)

  def __members(self):
      return (self.start, self.end)

  def __eq__(self, other):
      if type(other) is type(self):
          return self.__members() == other.__members()
      else:
          return False

  def __lt__(self, other):
    return self.start < other.start

  def __hash__(self):
      return hash(self.__members())

class GraphEdge:

  def __init__(self, start, end, start_point, end_point, w):
    self.start_node = start
    self.end_node = end
    self.subsequences_start = (start_point, start_point)
    self.subsequences_end = (end_point, end_point)
    self.weight = w

  def __str__(self):
   return 'StartNode: {}, EndNode: {}, StartSeq: {}, EndSeq: {}, Weight: {}'.format(self.start_node, self.end_node, self.subsequences_start, self.subsequences_end, self.weight) 
  
  def __members(self):
      return (self.start_node, self.end_node, self.subsequences_start, self.subsequences_end, self.weight)

  def __eq__(self, other):
      if type(other) is type(self):
          return self.__members() == other.__members()
      else:
          return False

  def __lt__(self, other):
    a = (self.subsequences_start, self.subsequences_end)
    b = (other.subsequences_start, other.subsequences_end)
    return a < b
  #def __hash__(self):
  #    return hash(self.__members())


class KNNGraph:
  nodes = set()
  adj_list = {}  
  def __init__(self, edges):
    for col, row, corr in edges:
      col_node = GraphNode(col, col)
      row_node = GraphNode(row, row)
      edge = GraphEdge(col_node, row_node, col, row, corr)
      back_edge = GraphEdge(row_node, col_node, row, col, corr)
      self.nodes.add(col_node)
      self.nodes.add(row_node)
      if col_node not in self.adj_list:
        self.adj_list[col_node] = {}
      if row_node not in self.adj_list:
        self.adj_list[row_node] = {}
      self.adj_list[col_node][row_node] = [edge]
      self.adj_list[row_node][col_node] = [back_edge]

  def __str__(self):
    result = ''
    for node in sorted(self.nodes, key=lambda x: x.start):
      edges_pretty = [str(edge) for sublist in self.adj_list[node].values() for edge in sublist] 
      result += 'Node: {}\nEdges:\n\t{}\n'.format(str(node), '\n\t'.join(edges_pretty))
    return result


  def is_consecutive(self, a, b):
    if not (b.start - a.end == 1 or a.start - b.end == 1):
      return False
    #print('Node {} is consecutive with node {}'.format(a,b))
    return True

  def num_consecutive_in_neighborhood(self, neighbors_a, neighbors_b):
    all_neighbors = [(x, True) for x in neighbors_a] + [(x, False) for x in neighbors_b]

    all_neighbors = sorted(all_neighbors, key=lambda x: x[0].start)

    i = 0
    corresponding = []
    while i < len(all_neighbors) - 1:
      node_1, is_a_1 = all_neighbors[i]
      node_2, is_a_2 = all_neighbors[i+1]
      if is_a_1 == is_a_2:
        i += 1
        continue
      if node_2.start - node_1.end == 1:
        if is_a_1:
          corresponding += (node_1, node_2)
        else:
          corresponding += (node_2, node_1)
      i += 1
    #print(corresponding)
    return len(corresponding)

  def num_consecutive_in_neighborhood_edge_aware(self, edges_a, edges_b):
    all_neighbors = [(x.subsequences_end[0], x.subsequences_end[1], True) for x in edges_a] + [(x.subsequences_end[0], x.subsequences_end[1], False) for x in edges_b]

    all_neighbors = sorted(all_neighbors, key=lambda x: x[0])

    i = 0
    corresponding = set()
    while i < len(all_neighbors) - 1:
      node_1_start, node_1_end, is_a_1 = all_neighbors[i]
      node_2_start, node_2_end, is_a_2 = all_neighbors[i+1]
      if is_a_1 == is_a_2:
        i += 1
        continue
      if node_2_start - node_1_end == 1:
        if is_a_1:
          corresponding.add((node_1_start, node_1_end, node_2_start, node_2_end))
        else:
          corresponding.add((node_2_start, node_2_end, node_1_start, node_1_end))
      i += 1
    #print(corresponding)
    return len(corresponding)
    

    
  def mergeable(self, a, b):
    if not self.is_consecutive(a,b):
      return False

    neighbors_a = [edge.end_node for edge in self.adj_list[a].values()]
    neighbors_b = [edge.end_node for edge in self.adj_list[b].values()]
    
    if len(neighbors_a) == 0 or len(neighbors_b) == 0:
      return False
 
    return self.num_consecutive_in_neighborhood(neighbors_a, neighbors_b) > 3

  def mergeable_edge_aware(self, a, b):
    if not self.is_consecutive(a,b):
      return False
  
    if self.adj_list[a] is None or self.adj_list[b] is None:
      return False

    if len(self.adj_list[a]) == 0 or len(self.adj_list[b]) == 0:
      return False

    edges_a = [item for sublist in self.adj_list[a].values() for item in sublist] 
    edges_b = [item for sublist in self.adj_list[b].values() for item in sublist] 
  
    result = self.num_consecutive_in_neighborhood_edge_aware(edges_a, edges_b)
    #return result >= min(len(edges_a), len(edges_b)) - 2
    return result >= 3


  def merge(self, a, b):
    #print('Merging node {} with node {}.'.format(a,b))
    edges_a = [item for sublist in self.adj_list[a].values() for item in sublist] 
    edges_b = [item for sublist in self.adj_list[b].values() for item in sublist] 
   


    neighbors_a = [x for x in self.adj_list[a].keys()]
    neighbors_b = [x for x in self.adj_list[b].keys()]
    
    new_node = GraphNode(min(a.start, b.start), max(a.end, b.end))
    self.nodes.add(new_node)
    self.adj_list[new_node] = {}

    new_neighbors = list(edges_a) + list(edges_b)

    for edge in new_neighbors:
      #print(edge)
      edge.start_node = new_node
      if edge.end_node == a or edge.end_node == b:
        continue
      if edge.end_node not in self.adj_list[new_node]:
        self.adj_list[new_node][edge.end_node] = []
      self.adj_list[new_node][edge.end_node].append(edge)

    #print(new_node)
    #print([str(node) for node in neighbors_a])
    #print([str(node) for node in neighbors_b])

    for node in neighbors_a + neighbors_b:
      if node == a or node == b:
        continue
      if node not in self.adj_list:
        print('Warning: node {} was not in adj list'.format(node))
        continue
      if new_node not in self.adj_list[node]:
        self.adj_list[node][new_node] = []
      if a in self.adj_list[node]:
        for old_edge in self.adj_list[node][a]:
          old_edge.end_node = new_node
          self.adj_list[node][new_node].append(old_edge)
        #print('Deleting {} from neighborhood of {}.'.format(a, node))
        del self.adj_list[node][a]
        #print('New edge: {}'.format(self.adj_list[node][new_node]))
      if b in self.adj_list[node]:
        for old_edge in self.adj_list[node][b]:
          old_edge.end_node = new_node
          self.adj_list[node][new_node].append(old_edge)
        #print('Deleting {} from neighborhood of {}.'.format(b, node))
        del self.adj_list[node][b]
    
    del self.adj_list[a]
    del self.adj_list[b]
    self.nodes.remove(a)
    self.nodes.remove(b)
    #print([str(x) for x in self.adj_list[new_node].values()])
 
    return new_node
    
  def are_consecutive_edges(self,a,b):
    if b.subsequences_start[0] == a.subsequences_start[1] + 1 and b.subsequences_end[0] == a.subsequences_end[1] + 1:
      return True
    if a.subsequences_start[0] == b.subsequences_start[1] + 1 and a.subsequences_end[0] == b.subsequences_end[1] + 1:
      return True
    return False
      
  def merge_edges_helper(self,a,b):
    a.subsequences_start = (min(a.subsequences_start[0], b.subsequences_start[0]), max(a.subsequences_start[1], b.subsequences_start[1]))
    a.subsequences_end = (min(a.subsequences_end[0], b.subsequences_end[0]), max(a.subsequences_end[1], b.subsequences_end[1]))
    a_count = a.subsequences_start[1] - a.subsequences_start[0] + 1
    b_count = b.subsequences_start[1] - b.subsequences_start[0] + 1
    a.weight = (a_count * a.weight + b_count * b.weight) / (a_count + b_count)
    return a
     
  
  def merge_edges(self, node):
    for elem in self.adj_list[node].keys():
      self.adj_list[node][elem] = sorted(self.adj_list[node][elem])
      curr = {}
      for item in self.adj_list[node][elem]:
        x = (item.subsequences_start[0] - 1, item.subsequences_start[1] - 1, item.subsequences_end[0] - 1, item.subsequences_end[1] - 1)
        y = (item.subsequences_start[0], item.subsequences_start[1], item.subsequences_end[0], item.subsequences_end[1])
        if x in curr:
          edge = self.merge_edges_helper(curr[x], item)
          del curr[x]
          curr[y] = edge
        else:
          curr[y] = item
       
        #if curr is None:
        #  curr = item
        #  continue
        #if self.are_consecutive_edges(curr, item):
        #  curr = self.merge_edges_helper(curr, item)
        #else:
        #  merged_edges.append(curr)
        #  curr = item
      self.adj_list[node][elem] = sorted(curr.values())
        
        
    
    #for end_node, edges in self.adj_list[node].items():
    #  for edge in edges:
    #    if curr is None:
    #      curr = edge
    #      continue
    #    #if is_edge_consecutive(curr, edge):
    #    #  self.adj_list[node][end_node]
      
      
    

  def maybe_merge(self,a,b):
    if not self.mergeable_edge_aware(a,b):
      print('Node {} and node {} not mergable'.format(a,b))
      return b 

    return self.merge(a, b)

  def combine(self):
    start_node = None
    for node in sorted(copy.copy(self.nodes)):
      if start_node is None:
        start_node = node
        continue
      start_node = self.maybe_merge(start_node, node)
    for x in self.nodes:
      self.merge_edges(x)
