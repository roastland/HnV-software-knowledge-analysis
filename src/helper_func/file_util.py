import json
import configparser
import re

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
    