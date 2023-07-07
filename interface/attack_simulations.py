from collections import deque
import heapq
import random
import re

# TODO we should have a class for storing the:
# - copy of attack graph/index
#   - with modified path_links
#   - target_node
# - attacker position

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
    
def all_neighbors_visited(neighbors, visited): 
    unvisited_neighbors = []
    for neighbor in neighbors:
        if neighbor not in visited:
            unvisited_neighbors.append(neighbor)
    return unvisited_neighbors

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
    if current != start_node:
        # reconstruct the path until the start node is reached
        while current in came_from.keys() and current != start_node:
            old_current = current
            # link from current -> old_current
            current = came_from[current]
            # condition for 'and' node       
            if len(current)>1:
                for node in current:
                    path_cost, _,  = reconstruct_path(came_from, node, start_node, costs, index, visited)
                    cost += path_cost+costs[old_current]
                    index[old_current]["path_links"].append(old_current)
                break
            else:
                current = current[0]
                if old_current not in visited:
                    cost += costs[old_current]
                    visited.add(old_current)
                if old_current not in index[current]["path_links"]:
                    index[current]["path_links"].append(old_current) 
    return cost, index, old_current
    


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
def get_costs(index):
    dict = {}
    for key in index.keys():
        node = index[key]
        if not node['ttc'] == None: # for the attacker node, the ttc is None
            dict[key]=node['ttc']['cost'][0]
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
Breadth-First Search (BFS), starting from the target node.
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

'''
BFS...for now it is basically a copy of get_heuristics_for_nodes()
This function returns all nodes which is at a lower distance than 'limit' cost
'''
def bfs(source, index, max_distance):
    nodes = {}
    queue = deque([(source, 0)])  # Start BFS from the start node with distance 0
    visited = set([source])  # Keep track of visited nodes
    # Perform Breadth-First Search (BFS) from the start node
    while queue:
        node, distance = queue.popleft()
        if distance > max_distance:
            break
        # reset the "path_links" attribute
        index[node]["path_links"] = index[node]["links"]
        # Assign the distance from the source for each node
        nodes[node] = index[node]  
        # Explore the neighbors of the current node
        for link in index[node]["links"]:
            if link not in visited:
                visited.add(link)
                queue.append((link, distance + index[link]['ttc']['cost'][0]))  # Increment the distance
    return nodes

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
    return dict 

# Cost to find the AND and OR path
def Cost(H, condition, weight):
    cost = {}
    if 'AND' in condition:
        AND_nodes = condition['AND']
        Path_A = ' AND '.join(AND_nodes)
        PathA = sum(H[node]+weight[node] for node in AND_nodes)
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
    if Start in Updated_cost.keys():
        values = Updated_cost[Start].values()
        if values:
            Min_cost = min(values)
            key = list(Updated_cost[Start].keys())
            Index = list(Updated_cost[Start].values()).index(Min_cost)
            Next = key[Index].split()
            if len(Next) == 1:
                Start = Next[0]
                path = shortest_path_ao_star(Start, Updated_cost, H)
                Path += '<--' + path
            else:
                if "AND" in Next:
                    Path += '<--(' + key[Index] + ') ['
                    for i in range(len(Next)):
                        if Next[i] == "AND":
                            continue
                        Start = Next[i]
                        path = shortest_path_ao_star(Start, Updated_cost, H)
                        Path += path
                        if i < len(Next) - 1:
                            Path += ' + '
                    Path += ']'
                else:
                    Path += '<--(' + key[Index] + ') '
                    Start = Next[0]
                    path = shortest_path_ao_star(Start, Updated_cost, H)
                    Path += path

    return Path

def calculate_shortest_path_cost(shortest_path_str, cost, heuristics):
    nodes = re.findall(r'\b\w+\b', shortest_path_str)
    total_cost = 0
    visited = set()

    for i, node in enumerate(nodes):
        if node == 'OR':
            if nodes.count(nodes[i-1]) > 1:
                visited.add(nodes[i-1])
                del nodes[i+1]
            elif nodes.count(nodes[i+1]) > 1:
                visited.add(nodes[i+1])
                del nodes[i-1]
            continue
        if node not in ['AND', 'OR'] and node not in visited:
            visited.add(node)
    # Calculate the total cost for visited nodes
    for node in visited:
        total_cost += cost[node] + heuristics[node]

    return total_cost

'''
Finds the shortest path with Dijkstra algorithm, with added conditions for handling the 'and' nodes.
'''
def dijkstra(start_node, target_node, index):

    node_ids = list(index.keys())

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
    
    costs = get_costs(index)
    costs_copy = costs.copy()

    current_node = start_node
    while len(open_set) > 0:
        # current_node is the node in open_set having the lowest f_score value
        current_score, current_node = heapq.heappop(open_set)
        visited.add(current_node)

        if current_node == target_node:
            return reconstruct_path(came_from, current_node, start_node, costs_copy, index, set())

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
    return 


''' 
calculate the random path (according to option 1)
'''
def random_path(start_node, target_node, index):
    node_ids = list(index.keys())

    visited = set()  # Store the IDs of visited nodes to avoid revisiting them
    visited.add(start_node)

    stack = [start_node]

    parent_nodes = get_parent_nodes_for_and_nodes(atkgraph)
    neighbor_nodes = get_neighbor_nodes(atkgraph)  # Get the linked nodes of the current node

    came_from = dict.fromkeys(node_ids, '')
    came_from = fill_dictionary_with_empty_list(came_from)

    costs = get_costs(index)
    cost = 0

    current_node = start_node
    while len(stack) > 0:
        current_node = stack.pop()
        print(current_node)

        if current_node == target_node:
            path = reconstruct_path(came_from, current_node, start_node, costs, index, set())
            return path

        links = index[current_node]['links']
        unvisited_links = all_neighbors_visited(links, visited)

        if len(unvisited_links)==0:
            while len(stack) > 0:
                current_node = stack.pop()
                links = index[current_node]['links']
                unvisited_links = all_neighbors_visited(links, visited)
                if len(unvisited_links)>0:
                    break
        if len(unvisited_links)>0:
                while True:
                    neighbor = random.choice(unvisited_links)
                    if all_parents_visited(neighbor, visited, index):
                        stack.append(neighbor)
                        visited.add(neighbor)
                        came_from[neighbor].append(current_node)
                        cost+=costs[neighbor]
                        break
    return 
   
def ao_star(atkgraph, target_node, index):
    atkgraph = get_parents_for_and_nodes(atkgraph)
    H = get_heuristics_for_nodes(atkgraph, target_node)
    weight = get_costs(index)
    and_nodes = get_and_nodes(atkgraph)
    adjacency_list = get_adjacency_list(atkgraph, and_nodes)
    Updated_cost = update_cost(H, adjacency_list, weight)
    shortest_path_str = shortest_path_ao_star(target_node, Updated_cost, H)
    total_cost = calculate_shortest_path_cost(shortest_path_str, weight, H)

    return shortest_path_str, total_cost