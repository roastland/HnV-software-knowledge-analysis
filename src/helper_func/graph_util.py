def transform_graph(graph):
    """
    Transforms the input graph into two dictionaries: nodes and edges.

    The function first creates a 'nodes' dictionary that maps each node's ID to its data. 
    Then, it creates an 'edges' dictionary that groups the edges by their labels, mapping each label to a list of edges with that label. 
    If an edge doesn't have a 'label', it joins the values in the 'labels' key with commas and uses it as the label. 
    This function could be useful for analyzing the graph based on the types of relationships (edge labels) present in the graph.

    Parameters:
    graph (dict): The input graph represented as a dictionary.

    Returns:
    tuple: A tuple containing two dictionaries. The first dictionary ('nodes') maps node IDs to node data. The second dictionary ('edges') maps edge labels to lists of edges with those labels.
    """
    nodes = { node['data']['id']: node['data'] for node in graph['elements']['nodes'] }
    edges = {}
    for edge in graph['elements']['edges']:
        if 'label' in edge['data']:
            label = edge['data']['label']
        else:
            label = ','.join(edge['data']['labels'])
            edge['data']['label'] = label
        if label not in edges:
            edges[label] = []
        edges[label].append(edge['data'])
    return (nodes, edges)


# def invert(edgeList):
#     prefix = "inv_"
#     invertedEdges = []
#     for edge in edgeList:
#         invertedEdge = {
#             'source': edge['target'],
#             'target': edge['source'],
#             'label': prefix + edge.get('label', ''),
#             **{key: value for key, value in edge.items() if key not in ['source', 'target', 'label']}
#         }
#         invertedEdges.append(invertedEdge)
#     return invertedEdges


def invert(edgeList):
    """
    Inverts the direction of edges in the input edge list.

    The function creates a new list of edges where the 'source' and 'target' of each edge are swapped. 
    It also prefixes the label of each edge with "inv_" to indicate that the edge has been inverted.
    
    Parameters:
    edgeList (list): The input list of edges. Each edge is represented as a dictionary.

    Returns:
    list: A new list of edges where the direction of each edge has been inverted and the label has been prefixed with "inv_".
    """
    prefix = "inv_"
    return [{**edge,
            'source': edge['target'],
            'target': edge['source'],
            'label': prefix + edge.get('label', 'edge'),
        } for edge in edgeList]


def find_paths(edgeList1, edgeList2):
    """
    Finds paths that connect edges from two different edge lists.

    The function first creates a mapping from the target to the source of each edge in the first edge list.
    Then, it iterates over the second edge list and checks if the source of each edge exists in the mapping.
    If it does, it creates a path from the source in the mapping, to the source and target of the current edge.
    It adds each path to a set to ensure uniqueness of paths.
    
    Parameters:
    edgeList1 (list): The first input list of edges. Each edge is represented as a dictionary.
    edgeList2 (list): The second input list of edges. Each edge is represented as a dictionary.

    Returns:
    set: A set of unique paths. Each path is represented as a tuple of three elements: the source from the mapping, the source of the edge, and the target of the edge.
    """
    source_mapping = {}
    for edge in edgeList1:
        source_mapping[edge['target']] = edge['source']

    paths = set()
    for edge in edgeList2:
        if edge['source'] in source_mapping:
            source1 = source_mapping[edge['source']]
            path = [source1, edge['source'], edge['target']]
            paths.add(tuple(path))

    return paths


def compose(l1, l2, newlabel=None):
    """
    Composes two lists of edges into a new list of edges.
    
    The function first creates a mapping from the source to the target, label, and weight of each edge in the second list.
    Then, it iterates over the first list and checks if the target of each edge exists in the mapping.
    If it does, it creates a new edge from the source of the edge in the first list to the target in the mapping.
    It also calculates a new weight as the product of the weights of the two edges.
    If the new edge already exists in the result, it adds the new weight to the existing weight.
    Otherwise, it adds the new edge to the result.
    
    Parameters:
    l1 (list): The first input list of edges. Each edge is represented as a dictionary.
    l2 (list): The second input list of edges. Each edge is represented as a dictionary.
    newlabel (str): An optional new label for the composed edges. If not provided, the labels of the two edges are concatenated with a hyphen.

    Returns:
    list: A new list of edges composed from the two input lists.
    """
    mapping = {
        edge['source']: {
            'target': edge['target'], 
            'label': edge.get('label','edge1'), 
            'weight': edge.get('properties', {}).get('weight', 1)
        } for edge in l2 }
    
    result = {}
    for edge in l1:
        s1 = edge['source']
        t1 = edge['target']
        label = edge.get('label', 'edge2')
        properties = edge.get('properties', {})
        mappingEntry = mapping.get(t1)

        if mappingEntry:
            newWeight = mappingEntry['weight'] * properties.get('weight', 1)
            key = (s1, mappingEntry['target'])
            if key not in result:
                result[key] = {
                    'source': s1,
                    'target': mappingEntry['target'],
                    'label': newlabel or label + "-" + mappingEntry['label'],
                    'properties': {'weight': newWeight},
                }
            else:
                result[key]['properties']['weight'] += newWeight
    return list(result.values())


def get_all_labels(objects):
    """
    Extracts all unique labels from a collection of objects.
    
    The function iterates over the input objects and checks if each object has a 'labels' key that is a list.
    If it does, it adds all labels from the list to a set to ensure uniqueness.
    
    Parameters:
    objects (dict): The input collection of objects. Each object is represented as a dictionary.

    Returns:
    set: A set of unique labels extracted from the input objects.
    """
    labels = set()
    for obj in objects.values():
        if 'labels' in obj and isinstance(obj['labels'], list):
            labels.update(obj['labels'])
    return labels


def get_edge_node_labels(edge, nodes):
    """
    Extracts the labels of the source and target nodes of an edge.
    
    The function first gets the labels of the source and target nodes from the nodes dictionary.
    Then, it creates a list of tuples where each tuple contains a label from the source node and a label from the target node.
    
    Parameters:
    edge (dict): The input edge represented as a dictionary.
    nodes (dict): The dictionary of nodes where keys are node IDs and values are node data.

    Returns:
    list: A list of tuples where each tuple contains a label from the source node and a label from the target node.
    """
    src_labels = nodes.get(edge['source'], {}).get('labels', [])
    tgt_labels = nodes.get(edge['target'], {}).get('labels', [])

    return [(src_label, tgt_label) for src_label in src_labels for tgt_label in tgt_labels]


def get_source_and_target_labels(edge_list, nodes):
    """
    Extracts the labels of the source and target nodes for each edge in a list of edges.
    
    The function iterates over the input list of edges and for each edge, it gets the labels of the source and target nodes.
    It adds each pair of source and target labels to a set to ensure uniqueness.
    
    Parameters:
    edge_list (list): The input list of edges. Each edge is represented as a dictionary.
    nodes (dict): The dictionary of nodes where keys are node IDs and values are node data.

    Returns:
    set: A set of unique pairs of source and target labels. Each pair is represented as a tuple.
    """
    edge_node_labels = {label for edge in edge_list for label in get_edge_node_labels(edge, nodes)}

    return edge_node_labels


def get_ontology(edges, nodes):
    """
    Constructs an ontology from a dictionary of edges and a dictionary of nodes.
    
    The function iterates over the input dictionary of edges and for each edge, it gets the labels of the source and target nodes.
    It maps each edge label to a set of unique pairs of source and target labels.
    
    Parameters:
    edges (dict): The input dictionary of edges where keys are edge labels and values are lists of edges.
    nodes (dict): The dictionary of nodes where keys are node IDs and values are node data.

    Returns:
    dict: A dictionary where keys are edge labels and values are sets of unique pairs of source and target labels. Each pair is represented as a tuple.
    """
    return {label: get_source_and_target_labels(edge, nodes) for label, edge in edges.items()}


def lift(rel1, rel2, newlabel=None):
    """
    Performs a 'lift' operation on two relations.
    
    The function first composes the two input relations, then composes the result with the inversion of the first relation.
    The 'lift' operation can be used in graph theory to create a new relation from two existing relations.
    
    Parameters:
    rel1 (list): The first input list of edges. Each edge is represented as a dictionary.
    rel2 (list): The second input list of edges. Each edge is represented as a dictionary.
    newlabel (str): An optional new label for the composed edges. If not provided, the labels of the two edges are concatenated with a hyphen.

    Returns:
    list: A new list of edges composed from the two input lists and the inversion of the first list.
    """
    return compose(compose(rel1, rel2), invert(rel1), newlabel)


def filter_objects_by_labels(data, labels):
    """
    Filters a collection of objects based on their labels.
    
    The function iterates over the input collection of objects and checks if any of the labels of each object are in the input list of labels.
    If they are, it adds the object to the filtered data.
    
    Parameters:
    data (dict): The input collection of objects. Each object is represented as a dictionary.
    labels (list): The input list of labels.

    Returns:
    dict: A dictionary of objects that have at least one label in the input list of labels.
    """
    filtered_data = {}
    for key, object in data.items():
        if any(label in labels for label in object['labels']):
            filtered_data[key] = object
    return filtered_data


def get_edges_with_labels(nodes, edge_list, label):
    """
    Filters a list of edges based on a specific label.
    
    The function iterates over the input list of edges and checks if the source and target nodes of each edge have the input label.
    If they do, it adds the edge to the filtered edges.
    
    Parameters:
    nodes (dict): The dictionary of nodes where keys are node IDs and values are node data.
    edge_list (list): The input list of edges. Each edge is represented as a dictionary.
    label (str): The input label.

    Returns:
    list: A list of edges where the source and target nodes have the input label.
    """
    filtered_edges = [edge for edge in edge_list if label in nodes[edge['source']].get('labels', []) and label in nodes[edge['target']].get('labels', [])]
    return filtered_edges


def extract_edges(edges, selected_nodes):
    """
    Extracts a list of edges that are connected to a selected list of nodes.

    The function iterates over the input list of edges and checks if the source and target node of each edge is in the selected list of nodes.
    If it is, it adds the edge to the extracted edges.

    Parameters:
    edges (list): The input list of edges. Each edge is represented as a dictionary.
    selected_nodes (list): The list of selected nodes.

    Returns:
    list: A list of edges where the source and target node is in the selected list of nodes.
    """
    extracted_edges = [edge for edge in edges if edge['source'] in selected_nodes and edge['target'] in selected_nodes]
    return extracted_edges
