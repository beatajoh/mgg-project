import math
import json
from collections import deque
import heapq
import random

'''
Discovers if the node is an 'and' or 'or' node.
If the node is an 'or' node, the function returns True.
If the node is an 'and' node, the function returns True if all parent nodes has been visited.
'''
def all_parents_visited(node, parent_nodes, visited):
    if is_and_node(node, parent_nodes):
        # if all the dependency steps (parents) are visited return true,
        # otherwise return false
        for parents in parent_nodes[node]:
            if parents not in visited:
                return False 
    return True
    
def all_neighbors_visited(neighbors, node, visited): 
    for neighbor in neighbors[node]:
        if neighbor not in visited:
            return False
    return True
'''
Returns true if the node is an and node.
'''
def is_and_node(node, parent_nodes):
    if node in parent_nodes:
       return True
    return False

'''
Reconstructs the path found by the Dijkstra function and calculates the total cost for the path.
'''
def reconstruct_path(came_from, current, start_node, costs, visited=set()):
    cost = 0
    total_path=[]
    if current != start_node:
        total_path = [current]
        # reconstruct the path until the start node is reached
        while current in came_from.keys() and current != start_node:
            old_current = current
            current = came_from[current] 
            # condition for 'and' node       
            if len(current)>1:
                for node in current:
                    path, costt = reconstruct_path(came_from, node, start_node, costs, visited)
                    total_path.insert(0,path)
                    cost += costt+costs[old_current]
                break
            else:
                current = current[0]
                # update cost for all nodes once
                if old_current not in visited:
                    cost += costs[old_current]
                    visited.add(old_current)
                total_path.insert(0,current)
    return total_path, cost


'''
def reconstruct_path(came_from, current, start_node, costs, visited=set()):
    cost = 0
    total_path=[]
    if current != start_node:
        total_path = [current]
        # reconstruct the path until the start node is reached
        while current in came_from.keys() and current != start_node:
            old_current = current
            current = came_from[current] 
            # condition for 'and' node       
            if len(current)>1:
                for node in current:
                    path, costt = reconstruct_path(came_from, node, start_node, costs, visited)
                    total_path.insert(0,path)
                    cost += costt+costs[old_current]
            else:
                current = current[0]
                # update cost for all nodes once
                if old_current not in visited:
                    cost += costs[old_current]
                    visited.add(old_current)
                total_path.insert(0,current)
    print(total_path)
    return total_path, cost
'''

'''
Returns a list of node ids.
'''
def get_node_ids(atkgraph):
    list = []
    for node in atkgraph:
        list.append(node['id'])
    return list

'''
Fills a dictionary.
Returns a dictionary with node ids as keys, with empty list as the values.
'''
def fill_dictionary_with_empty_list(dict):
    for key in dict.keys():
        dict[key] = list()
    return dict

'''
Gets the neighbor nodes, aka the outgoing links to nodes, for all nodes in the attack graph.
Returns a dictionary with node ids as keys, and score as values.
'''
def get_neighbor_nodes(atkgraph): 
    dict = {}
    for node in atkgraph:
        dict[node['id']] = node['links']
    return dict

'''
Gets the parent nodes, aka the incoming links to nodes, for all nodes in the attack graph.
Returns a dictionary with node ids as keys, and the parent_list as values.
'''
def get_parent_nodes_for_and_nodes(atkgraph): 
    dict = {}
    for node in atkgraph:
        if node['type'] == 'and':
            dict[node['id']] = node['parent_list']
    return dict

'''
Gets the cost for all attack steps in the graph.
Returns a dictionary with node ids as keys, and the parent_list as values.
'''
def get_costs_for_nodes(atkgraph):
    dict = {}
    for node in atkgraph:
        if not node['ttc'] == None: # for the attacker node, the ttc is None
            dict[node['id']]=node['ttc']['cost'][0]
    return dict


'''
Traverse the attack graph .json file and get all parents to 'and' nodes and add new 'parent_list' attribute to the file.
parent_list is an array of attack step ids.
'''
def get_parents_for_and_nodes(atkgraph):
    n=0
    id=""
    id2=""
    for i, node in enumerate(atkgraph):
        id=node["id"]
        parent_list=[]
        if node["type"]=="and":
            for node2 in atkgraph:
                id2=node2["id"]
                for link in node2["links"]:
                    if link==id and node2["type"] in ["and", "or"]:
                        parent_list.append(id2)
            n+=1
            atkgraph[i]["parent_list"]=parent_list
        else:
            for node2 in atkgraph:
                id2=node2["id"]
                for link in node2["links"]:
                    if link==id and node2["type"] in ["and", "or"]:
                        parent_list.append(id2)
            n+=1
            atkgraph[i]["parent_list"]=parent_list
    return atkgraph

'''
Performing a graph traversal algorithm, 
breadth-first search (BFS), starting from the target node.
'''
def get_heuristics_for_nodes(atkgraph, target_node):
    heuristics = {}
    
    # Perform Breadth-First Search (BFS) from the target node
    queue = deque([(target_node, 0)])  # Start BFS from the target node with distance 0
    visited = set([target_node])  # Keep track of visited nodes

    while queue:
        node, distance = queue.popleft()
        heuristics[node] = distance  # Assign the distance as the heuristic value
        # Explore the neighbors of the current node
        for other_node in atkgraph:
            if other_node['id'] == node:
                parent_list = other_node['parent_list']
                break    
        for parent in parent_list:
            if parent not in visited:
                visited.add(parent)
                queue.append((parent, distance + 1))  # Increment the distance by 1 for each neighbor
    
    return heuristics

def get_adjacency_list(atkgraph, and_nodes):
    dict = {}
    or_and = ''
    for node in atkgraph:
        adjacent = {}
        if node['id'] in and_nodes:
            or_and = 'AND'
        else: 
            or_and = 'OR'
        adjacent[or_and] = []
        for parent in node['parent_list']:
            adjacent[or_and].append(parent)
        dict[node['id']] = adjacent
    # print("the result", dict)
    return dict 

# Cost to find the AND and OR path
def Cost(H, condition, weight):
    cost = {}
    if 'AND' in condition:
        AND_nodes = condition['AND']
        Path_A = ' AND '.join(AND_nodes)
        PathA = max(H[node]+weight[node] for node in AND_nodes)  # Calculate the maximum cost instead of summing
        cost[Path_A] = PathA

    if 'OR' in condition:
        OR_nodes = condition['OR']
        if OR_nodes:
            Path_B =' OR '.join(OR_nodes)
            PathB = min(H[node]+weight[node] for node in OR_nodes)
            cost[Path_B] = PathB

    return cost


# Update the cost
def update_cost(H, Conditions, weight):
    Main_nodes = list(Conditions.keys())
    Main_nodes.reverse()
    least_cost= {}
    for key in Main_nodes:
        condition = Conditions[key]
        print(key,':', Conditions[key],'>>>', Cost(H, condition, weight))
        c = Cost(H, condition, weight)
        if c:
            H[key] = min(c.values())
        least_cost[key] = Cost(H, condition, weight)
    return least_cost

def get_and_nodes(atkgraph):
    list = set()
    for node in atkgraph:
        if node['type'] == 'and':
            list.add(node['id'])
    return list  

'''
AO * Shortest path function
'''
def shortest_path_ao_star(Start, Updated_cost, H):
    Path = Start
    total_cost = H[Start]  # Initialize total cost with the cost of the starting node

    if Start in Updated_cost.keys():
        values = Updated_cost[Start].values()
        if values:
            Min_cost = min(values)
            key = list(Updated_cost[Start].keys())
            Index = list(Updated_cost[Start].values()).index(Min_cost)

            Next = key[Index].split()

            if len(Next) == 1:
                Start = Next[0]
                path, cost = shortest_path_ao_star(Start, Updated_cost, H)
                Path += '<--' + path
                total_cost = H[Start] + cost  # Corrected line
            else:
                if "AND" in Next:
                    Path += '<--(' + key[Index] + ') ['
                    and_costs = []  # Initialize a list to store costs for AND nodes
                    for i in range(len(Next)):
                        if Next[i] == "AND":
                            continue
                        Start = Next[i]
                        path, cost = shortest_path_ao_star(Start, Updated_cost, H)
                        Path += path
                        total_cost += cost
                        and_costs.append(cost)  # Store costs for AND nodes
                        if i < len(Next) - 1:
                            Path += ' + '
                    Path += ']'
                    if len(and_costs) > 1:
                        total_cost -= sum(and_costs) - min(and_costs)  # Subtract the sum of AND node costs except the minimum
                else:
                    Path += '<--(' + key[Index] + ') '
                    Start = Next[0]
                    path, cost = shortest_path_ao_star(Start, Updated_cost, H)
                    Path += path
                    total_cost = H[Start] + cost  # Corrected line

    return Path, total_cost

'''
Finds the shortest path with Dijkstra algorithm, with added conditions for handling the 'and' nodes.
'''
def dijkstra(atkgraph, start_node, target_node):
    node_ids = get_node_ids(atkgraph)

    open_set = []
    heapq.heappush(open_set, (0, start_node))

    visited = set()
    visited.add(start_node)

    came_from = dict.fromkeys(node_ids, '')
    came_from = fill_dictionary_with_empty_list(came_from)

    # g_score is a map with default value of infinity
    g_score = dict.fromkeys(node_ids, 10000)
    g_score[start_node] = 0

    # calculate the h_score for all nodes
    h_score = dict.fromkeys(node_ids, 0)
   

    # for node n, f_score[n] = g_score[n] + h_score(n). f_score[n] represents our current best guess as to
    # how cheap a path could be from start to finish if it goes through n.
    f_score = dict.fromkeys(node_ids, 0)
    f_score[start_node] = h_score[start_node]
    
    costs = get_costs_for_nodes(atkgraph)
    costs_copy = get_costs_for_nodes(atkgraph)
    neighbor_nodes = get_neighbor_nodes(atkgraph)
    parent_nodes = get_parent_nodes_for_and_nodes(atkgraph)

    current_node = start_node
    while len(open_set) > 0:
        # current_node is the node in open_set having the lowest f_score value
        current_score, current_node = heapq.heappop(open_set)
        visited.add(current_node)

        if current_node == target_node:
            return reconstruct_path(came_from, current_node, start_node, costs_copy, set())

        current_neighbors = neighbor_nodes[current_node]
       
        for neighbor in current_neighbors:  
            tentative_g_score = g_score[current_node]+costs[neighbor]
            # try the neighbor node with a lower g_score than the previous node
            if tentative_g_score < g_score[neighbor]:
                # if it is an 'or' node or if the and all parents to the 'and' node has been visited,
                # continue to try this path
                if all_parents_visited(neighbor, parent_nodes, visited):
                    came_from[neighbor].append(current_node)
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + h_score[neighbor]
                    if neighbor not in open_set:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
                # if the node is an 'and' node, still update the node cost and keep track of the path
                elif is_and_node(neighbor, parent_nodes):
                    costs[neighbor]=tentative_g_score
                    came_from[neighbor].append(current_node)
    return "Path not found"


''' 
calculate the random path (according to option 1)
'''
def random_path(atkgraph, start_node, target_node):
    node_ids = get_node_ids(atkgraph)

    visited = set()  # Store the IDs of visited nodes to avoid revisiting them
    visited.add(start_node)

    stack = [start_node]

    parent_nodes = get_parent_nodes_for_and_nodes(atkgraph)
    neighbor_nodes = get_neighbor_nodes(atkgraph)  # Get the linked nodes of the current node

    came_from = dict.fromkeys(node_ids, '')
    came_from = fill_dictionary_with_empty_list(came_from)

    costs = get_costs_for_nodes(atkgraph)
    cost = 0

    current_node = start_node
    while current_node != target_node:
       
        # all paths has been tried
        if len(stack) == 0: 
            return "Path not found"
        # leaf in graph
        if len(neighbor_nodes[current_node]) == 0: 
            current_node = stack.pop()
    
        # select a node from the neighbor list
        neighbor = random.choice(neighbor_nodes[current_node])

        # a node which has not been visited yet was selected
        if neighbor not in visited:
            if all_parents_visited(neighbor, parent_nodes, visited):
                came_from[neighbor].append(current_node)
                stack.append(current_node)
                current_node = neighbor
                visited.add(neighbor)
                cost+=costs[current_node]
            else: 
                # 'and' node was found
                current_node = stack.pop()
                continue
        # a node which has been visited previously was selected
        elif neighbor in visited:
            # if we have tried all paths forward already, move to previous node in path
            if all_neighbors_visited(neighbor_nodes, current_node, visited):
                current_node = stack.pop()
    
    path = reconstruct_path(came_from, current_node, start_node, costs, set())
    print("Real cost: ", cost)
    print("Visited nodes: ", visited)

    return path
  
   
def ao_star(atkgraph, target_node):
    atkgraph = get_parents_for_and_nodes(atkgraph)
    H = get_heuristics_for_nodes(atkgraph, target_node)
    weight = get_costs_for_nodes(atkgraph)
    and_nodes = get_and_nodes(atkgraph)
    adjacency_list = get_adjacency_list(atkgraph, and_nodes)
    Updated_cost = update_cost(H, adjacency_list, weight)
    shortest_path_str, total_cost = shortest_path_ao_star(target_node, Updated_cost, H)

    return shortest_path_str, total_cost