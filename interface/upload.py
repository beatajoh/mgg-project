from py2neo import Graph, Node, Relationship
import json


def upload_json_to_neo4j_database(file, graph):   # add file as argument
    nodes = {}
    graph.delete_all()
    with open(file, 'r') as file:
        data = json.load(file)
    for node in data:
        costt = 0
        if node["ttc"] != None:
            costt = node["ttc"]["cost"][0]
        # build Node object
        node_obj = Node(
            str(node["horizon"]),
            name=node["id"],
            type=node["type"],
            objclass=node["objclass"],
            objid=node["objid"],
            atkname=node["atkname"],
            is_traversable=node["is_traversable"],
            is_reachable=node["is_reachable"],
            graph_type = "attackgraph",
            cost = costt
        )
        graph.create(node_obj)
        nodes[node["id"]] = node_obj

    for node in data:
        links = node["path_links"]
        for link in links:
            if link in nodes.keys():
                from_node = nodes[node["id"]]
                to_node = nodes[link]
                relationship = Relationship(from_node, "Relationship", to_node)
                graph.create(relationship)

