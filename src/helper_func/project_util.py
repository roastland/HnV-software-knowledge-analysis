import json
import configparser
import re
from src.helper_func.graph_util import *

def read_json_file(file_path):
    with open(file_path, 'rb') as file:
        data = json.load(file)
    return data

def parse_json(json_string):
    json_dict = json.loads(json_string)
    return json_dict

def prettify_json(obj):
    pretty_json = json.dumps(obj, indent=2)
    return pretty_json

def write_to_json_file(obj, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(obj, json_file, indent=2)

def read_ini_file(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    ini_dict = {section: dict(config.items(section))
                for section in config.sections()}
    return ini_dict


def remove_java_comments(java_source):
    # Regular expression to match Java comments (both single-line and multi-line)
    pattern = r"(//.*?$)|(/\*.*?\*/)"

    # Remove comments using the regular expression
    java_source_without_comments = re.sub(
        pattern, "", java_source, flags=re.MULTILINE | re.DOTALL)

    return java_source_without_comments.strip()


def sentence(s):
    '''
    Capitalize the first letter of a string `s` and ensures that the string 
    ends with a period (if it's not already a sentence-ending punctuation).
    '''
    t = s.strip()
    if t[-1] in '.?!…~–—':
        return f'{t[0].upper()}{t[1:]}'
    else:
        return f'{t[0].upper()}{t[1:]}.'
    

def setup(filepath):
    """
    Sets up the project configuration, reads the input file, transforms the graph, and prepares the OpenAI client arguments.

    Args:
        filepath (str): The path to the configuration file.

    Returns:
        tuple: A tuple containing seven elements:
            - project_name (str): The name of the project.
            - project_desc (str): The description of the project.
            - graph (dict): The graph data read from the input file.
            - nodes (dict): The nodes in the transformed graph.
            - edges (dict): The edges in the transformed graph.
            - client_args (dict): The arguments for the OpenAI client.
            - model (str): The OpenAI model to be used.
    """
        
    config = read_ini_file(filepath)
    project_name = config['project']['name']
    project_desc = config['project']['desc']
    ifile = config['project']['ifile']
    
    graph = read_json_file(ifile)
    nodes,edges = transform_graph(graph)
    
    client_args = dict()

    if 'apikey' in config['openai']:
        client_args['api_key'] = config['openai']['apikey']
    if 'apibase' in config['openai']:
        client_args['base_url'] = config['openai']['apibase']
    if 'model' in config['openai']:
        model = config['openai']['model']
    else:
        model = "gpt-3.5-turbo"
    
    return project_name, project_desc, graph, nodes, edges, client_args, model


def elements_preparation(nodes, edges):
    """
    Prepares the elements of a software project for Automated Source Code Summarization (ASCS) and layering.

    Args:
        nodes (dict): A dictionary representing the nodes in the software knowledge graph, where each node is a package, class, or method.
        edges (dict): A dictionary representing the edges in the software knowledge graph, where each edge represents a relationship between two nodes.

    Returns:
        tuple: A tuple containing two elements:
            - hierarchy (dict): A hierarchy of packages, classes, and methods in the project, where each package contains classes and each class contains methods.
            - nodes (dict): The updated nodes dictionary with added 'description' key for each method, class, and package.
    """
    
    methods = sorted(find_paths(edges['contains'], edges['hasScript']))
    print('Methods count: {}'.format(len(methods)))
    classes = sorted({(pkg,clz) for pkg,clz,_ in methods})
    print('Classes count: {}'.format(len(classes)))
    packages = sorted({pkg for pkg,_ in classes})
    print('Packages count: {}'.format(len(packages)))
    
    for _,_,met_id in methods:
        if nodes[met_id]['properties'].get('description') is None:
            nodes[met_id]['properties']['description'] = None
    for _,cls_id in classes:
        if nodes[cls_id]['properties'].get('description') is None:
            nodes[cls_id]['properties']['description'] = None
    for pkg_id in packages:
        if nodes[pkg_id]['properties'].get('description') is None:
            nodes[pkg_id]['properties']['description'] = None
    
    hierarchy = {
        pkg_id: { 
            cls_id: [
                met_id for _,c,met_id in methods if c == cls_id
            ] for p,cls_id in classes if p == pkg_id
        } for pkg_id in packages
    }
    
    print('Project hierarchy count: {}'.format(len(hierarchy)))
       
    return hierarchy, nodes
    

def lower1(s):
    """
    Converts the first character of a string to lowercase.

    Args:
        s (str): The input string.

    Returns:
        str: The string with the first character converted to lowercase. If the input string is empty, it is returned as is.
    """
    
    if not s:
        return s
    return s[0].lower() + s[1:]


def describe(node):
    """
    Generates a description for a node in the software knowledge graph.

    Args:
        node (dict): The node for which to generate a description.

    Returns:
        str: A string containing the description of the node, formatted as a series of key-value pairs.
    """
    
    keys = 'description,reason,howToUse,howItWorks,assertions,roleStereotype,layer'.split(',')
    desc = ''
    for key in keys:
        if key in node['properties']:
            desc += f"**{key}**: {str(node['properties'][key])}. "
    return desc
