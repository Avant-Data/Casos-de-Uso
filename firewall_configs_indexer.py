from collections import Counter
import concurrent.futures
import socket
import logging
import requests
import re
import hashlib
import json
from typing import Optional, Union, List, Tuple, Set, Any
import xmltodict

API_KEY = 'SUA KEY API'
POST_URL = 'URL DO AVANTDATA EX: https://avantdata.com.br/'
FIREWALL_API = 'URL DA API DO FIREWALL EX: https://192.000.000.000/api'
TEMPLATE_NAME_RULES = 'firewall_rules'
TEMPLATE_NAME_SESSION = 'firewall_session'
TEMPLATE_NAME_NETWORK = 'firewall_network'
TEMPLATE_NAME_HEALTH = 'firewall_health'
TEMPLATE_NAME_AUTH = 'firewall_auth'
TEMPLATE_ALIASES = 'Firewall_Compliance'
IGNORE_KEYS = ['latest', 'icmp-unreachable', 'rule-type', 'disabled']


PAYLOADS = {
    'schedule': {
        'type': 'config',
        'action': 'get',
        'key': API_KEY,
        'xpath': '/config/devices/entry/vsys/entry/schedule'
    },
    'configs': {
        'type': 'config',
        'action': 'get',
        'key': API_KEY,
        'xpath': '/config/devices/entry/vsys/entry/rulebase/security/rules'
    },
    'hits': {
        'type': 'op',
        'cmd': "<show><rule-hit-count><vsys><vsys-name><entry name='vsys1'><rule-base><entry name='security'><rules><all></all></rules></entry></rule-base></entry></vsys-name></vsys></rule-hit-count></show>",
        'key': API_KEY,
    },
    'session': {
        'type': 'op',
        'cmd': '<show><session><info></info></session></show>',
        'key': API_KEY,
    },
    'top': {
        'type': 'op',
        'cmd': '<show><system><resources></resources></system></show>',
        'key': API_KEY,
    },
    'dataplane': {
        'type': 'op',
        'cmd': '<show><running><resource-monitor><hour><last>1</last></hour></resource-monitor></running></show>',
        'key': API_KEY,
    },
    'auth': {
        'type': 'config',
        'action': 'get',
        'key': API_KEY,
        'xpath': '/config/mgt-config/users/entry'
    },
    'roles': {
        'type': 'config',
        'action': 'get',
        'key': API_KEY,
        'xpath': '/config/shared/admin-role'
    },
    'network': {
        'type': 'op',
        'cmd': '<show><interface>all</interface></show>',
        'key': API_KEY,
    }
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning)


def script():
    firewall_data = get_firewall_data(PAYLOADS)
    # health
    data_health = prepare_data_health(firewall_data, 'dataplane', 'top')
    data_health = add_id_type_index(data_health, TEMPLATE_NAME_HEALTH)
    upload_avantdata(data_health, TEMPLATE_NAME_HEALTH, custom={
                **{float_item:'float' for float_item in [
                    '1min', '5min', '15min', 'userSpacePercentage', 'systemSpacePercentage',
                    'idlePercentage', 'waitPercentage', 'stolenTimePercentage',
                    'totalMB', 'freeMB', 'usedMB', 'buffCacheMB',
                    'virtualMemoryMB', 'residentSetSizeMB', 'sharedMemoryMB',
                    'cpuPercentage', 'memoryPercentage', 'dataplaneLoadAverage1Hour'
                ]},
                **{int_item:'integer' for int_item in [
                    'processID', 'priority', 'cumulativeTime'
                ]},
             })
    # session
    data_session = prepare_data_sessions(firewall_data, 'session')
    data_session = add_id_type_index(data_session, TEMPLATE_NAME_SESSION)
    upload_avantdata(data_session, TEMPLATE_NAME_SESSION)
    # rules
    data_rules = prepare_data_rules(firewall_data, 'configs', 'hits', 'schedule')
    data_rules = add_id_type_index(data_rules, TEMPLATE_NAME_RULES)
    upload_avantdata(data_rules, TEMPLATE_NAME_RULES, custom={
                'logStart': 'boolean',
                'enabled': 'boolean',
                'logging': 'boolean',
                'hitCount': 'int',
                'lastHitTimestamp': 'date',
                'lastResetTimestamp': 'date',
                'firstHitTimestamp': 'date'
             })
    # auth
    data_auth = prepare_data_auth(firewall_data, 'auth', 'roles')
    data_auth = add_id_type_index(data_auth, TEMPLATE_NAME_AUTH)
    upload_avantdata(data_auth, TEMPLATE_NAME_AUTH)
    # network
    data_network = prepare_data_network(firewall_data, 'network')
    data_network = add_id_type_index(data_network, TEMPLATE_NAME_NETWORK)
    upload_avantdata(data_network, TEMPLATE_NAME_NETWORK)


def get_firewall_data(payloads):
    session = requests.Session()
    data_dict = dict()
    for index, payload in payloads.items():
        logger.info('Connecting to firewall and searching for {}'.format(index))
        response = session.get(FIREWALL_API, params=payload, verify=False)
        if response.status_code == 200:
            xml_data = xmltodict.parse(response.text)
            logger.info('{} loaded'.format(index))
            data_dict.update({index: xml_data})
        else:
            logger.info('Error: Unable to retrieve {}. Status code: {}'.format(
                index, response.status_code))
    session.close()
    return json.loads(json.dumps(data_dict))


def prepare_data_rules(data, config, hits, schedule):
    data_list = []
    rules_entries = force_list(data.get(config, {}).get('response', {}).get(
        'result', {}).get('rules', {}).get('entry', []))
    hits_entries = {entry.get('@name'): entry for entry in data.get(hits, {}).get('response', {}).get('result', {}).get(
        'rule-hit-count', {}).get('vsys', {}).get('entry', {}).get('rule-base', {}).get('entry', {}).get('rules', {}).get('entry', [])}
    schedule_entries_list = force_list(data.get(schedule, {}).get('response', {}).get(
        'result', {}).get('schedule', {}).get('entry', []))
    schedule_entries = {}
    for entry in schedule_entries_list:
        name = entry['@name']
        schedule_entries[name] = {'name': name}
        schedule_entries[name].update(
            {key: value for key, value in entry.items() if key != '@name'})
    for rule in rules_entries:
        if rule.get('@name') in hits_entries.keys():
            rule.update(hits_entries.get(rule.get('@name')))
            for timestamp_item in ['last-hit-timestamp', 'last-reset-timestamp', 'first-hit-timestamp']:
                if timestamp_item in hits_entries.get(rule.get('@name')):
                    rule.update({timestamp_item: int(
                        rule.get(timestamp_item))*1000})
        rule.pop('latest')
        if rule.get('log-setting'):
            rule['logging'] = True
        else:
            rule['logging'] = False
        if rule.get('schedule') in schedule_entries.keys():
            rule['schedule'] = force_list(
                schedule_entries.get(rule.get('schedule')))
        if rule.get('disabled'):
            if rule['disabled'] == 'yes':
                rule['enabled'] = False
        else:
            rule['enabled'] = True
        for key in ['log-start', 'log-end']:
            rule[key] = yes_no_to_bool(rule, key)
        for ignore_key in IGNORE_KEYS:
            rule.pop(ignore_key, None)
        rule = convert_keys_to_camel_case(rule)
        rule = transform_keys_and_force_member_to_list(rule)
        data_list.append(rule)
    return data_list


def prepare_data_sessions(data, session):
    data_list = []
    session_entries = force_list(data.get(session, {}).get('response', {}).get(
        'result', {}))
    for session_entry in session_entries:
        session_entry = convert_keys_to_camel_case(session_entry)
        data_list.append(session_entry)
    return data_list


def prepare_data_health(data, dataplane, top):
    data_list = []
    top_result = data.get(top, {}).get('response', {}).get('result', '')
    top_json = parse_top(top_result)
    dataplane_entry = data.get(dataplane, {}).get(
        'response', {}).get('result', {})
    cpu_load_average = dataplane_entry.get('resource-monitor', {}).get('data-processors', {}).get(
        'dp0', {}).get('hour', {}).get('cpu-load-average', {}).get('entry', [])
    values_load = [int(x.get('value', 0)) for x in cpu_load_average]
    average_load = sum(values_load) / len(values_load)
    top_json.update({'dataplaneLoadAverage1Hour': average_load})
    data_list.append(top_json)
    return data_list


def prepare_data_auth(data, auth, roles):
    data_list = []
    auth_entries = force_list(data.get(auth, {}).get(
        'response', {}).get('result', {}).get('entry', []))
    roles_entries = {entry.get('@name'): entry for entry in force_list(data.get(
        roles, {}).get('response', {}).get('result', {}).get('admin-role', {}).get('entry', []))}
    for user in auth_entries:
        if user.get('permissions', {}).get('role-based', {}).get('custom', {}).get('profile'):
            user['permissions']['role-based']['custom']['profile'] = roles_entries.get(
                user['permissions']['role-based']['custom']['profile'], user['permissions']['role-based']['custom']['profile'])
        auth_dict = {'name': user.get('@name'),
                     'permissions': user.get('permissions'),
                     'authentication-profile': user.get('authentication-profile', '')
                     }
        auth_dict = convert_keys_to_camel_case(auth_dict)
        auth_dict = transform_keys_and_force_member_to_list(auth_dict)
        data_list.append(auth_dict)
    return data_list


def prepare_data_network(data, network):
    data_list = []
    network_ifnet = force_list(data.get(network, {}).get(
        'response', {}).get('result', {}).get('ifnet', {}).get('entry', []))
    network_hw = force_list(data.get(network, {}).get(
        'response', {}).get('result', {}).get('hw', {}).get('entry', []))
    payloads_interfaces = {
        interface: {
            'type': 'op',
            'cmd': '<show><interface>{}</interface></show>'.format(interface),
            'key': API_KEY,
        } for interface in set([entry.get('name') for entry in network_ifnet+network_hw])
    }
    detailed_data = get_firewall_data(payloads_interfaces)
    for interface, response in detailed_data.items():
        interface_dict = {
            'name': interface,
            **remove_null_values(response.get('response', {}).get('result', {}))
        }
        interface_dict = convert_keys_to_camel_case(interface_dict)
        data_list.append(interface_dict)
    return data_list


def add_id_type_index(data_list, template):
    new_data_list = []
    for data in data_list:
        new_data_list.append({
            **data,
            'id': generateID(data),
            'type': template,
            'index': template
        })
    return new_data_list


def yes_no_to_bool(obj, key):
    if obj.get(key):
        if obj[key] == 'yes':
            return True
    return False

def generateID(data: Any) -> str:
    if type(data) is not str:
        import json
        data = json.dumps(data)
    return hashlib.md5(data.encode('utf-8')).hexdigest()


def force_list(obj):
    if isinstance(obj, (list, tuple, set)):
        return obj
    return [obj]

def remove_null_values(obj):
    if isinstance(obj, dict):
        for key in list(obj.keys()):
            value = obj[key]
            if value is None:
                del obj[key]
            else:
                obj[key] = remove_null_values(value)
        return obj
    elif isinstance(obj, list):
        return [remove_null_values(item) for item in obj]
    else:
        return obj

def transform_keys_and_force_member_to_list(obj):
    if isinstance(obj, dict):
        new_obj = {}
        for key, value in obj.items():
            if key == "@Name":
                new_obj["name"] = value
            elif key == "to":
                new_obj["zoneSource"] = value
            elif key == "from":
                new_obj["zoneDestination"] = value
            elif key == "source":
                new_obj["objectSource"] = value
            elif key == "destination":
                new_obj["objectDestination"] = value
            elif key == "source-user":
                new_obj["userSource"] = value
            elif key == "category":
                new_obj["URLCategory"] = value
            elif key == "member":
                if not isinstance(value, list):
                    new_obj[key] = [value]
                else:
                    new_obj[key] = value
            else:
                new_obj[key] = transform_keys_and_force_member_to_list(value)
        return new_obj
    else:
        return obj


def parse_top(top_output):
    lines = top_output.split("\n")
    top_line = lines[0].strip()
    top_line_data = re.split(r'\s+', top_line)
    load_avg = top_line_data[-3:]
    cpu_line = lines[2].strip()
    cpu_data = re.findall(r'(\d+\.\d+)%', cpu_line)
    memory_line = lines[3].strip()
    memory_data = re.findall(r'(\d+)k', memory_line)
    processes = []
    process_pattern = re.compile(
        r'^\s*(\d+)(?:\s+([\w-]+))?\s+(\d+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+([RSDZTW])\s+(\S+)\s+(\S+)\s+(\S+)\s+(.+)$'
    )
    for line in lines[7:]:
        if not line:
            continue
        process_match = process_pattern.match(line)
        if process_match:
            process = {
                'processID': int(process_match.group(1)),
                'user': process_match.group(2) or '',
                'priority': int(process_match.group(3)),
                'nice': process_match.group(4),
                'virtualMemoryMB': convert_to_mb(process_match.group(5)),
                'residentSetSizeMB': convert_to_mb(process_match.group(6)),
                'sharedMemoryMB': convert_to_mb(process_match.group(7)),
                'processState': {'R': 'running', 'S': 'sleeping', 'Z': 'zombie'}.get(process_match.group(8), process_match.group(8)),
                'cpuPercentage': float(process_match.group(9)),
                'memoryPercentage': float(process_match.group(10)),
                'cumulativeTime': convert_time_to_milliseconds(process_match.group(11)),
                'command': process_match.group(12).strip()
            }
            processes.append(process)
    parsed_output = {
        'loadAvg': {min: float(avg.replace(',', '')) for min, avg in zip(['1min', '5min', '15min'], load_avg)},
        'cpuUsage': {
            'userSpacePercentage': float(cpu_data[0]),
            'systemSpacePercentage': float(cpu_data[1]),
            'idlePercentage': float(cpu_data[2]),
            'waitPercentage': float(cpu_data[3]),
            'stolenTimePercentage': float(cpu_data[4])
        },
        'memoryUsage': {
            'totalMB': float(memory_data[0])/1024,
            'freeMB': float(memory_data[1])/1024,
            'usedMB': float(memory_data[2])/1024,
            'buffCacheMB': float(memory_data[3])/1024
        },
        'processes': processes
    }
    return parsed_output


def convert_time_to_milliseconds(time_str):
    try:
        minutes, seconds = time_str.split(':')
        total_seconds = int(minutes) * 60 + float(seconds)
        return int(total_seconds * 1000)
    except Exception:
        return 0


def convert_to_mb(value):
    units = {'k': 1/1024, 'm': 1, 'g': 1024}
    suffix = value[-1].lower()
    if suffix in units and is_int_or_float(value[:-1]):
        return float(value[:-1])*units[suffix]
    else:
        return float(value)/1024


def is_int_or_float(x):
    try:
        float_x = float(x)
    except ValueError:
        return False
    return isinstance(float_x, (int, float))


def camel_case(s: str) -> str:
    if s:
        s = re.sub(r'(_|-)+', ' ', str(s)).title().replace(' ', '')
        return ''.join([s[0].lower(), s[1:]])
    return s


def convert_keys_to_camel_case(obj):
    if isinstance(obj, dict):
        return {
            camel_case(key): convert_keys_to_camel_case(value)
            for key, value in obj.items()
        }
    elif isinstance(obj, list):
        return [convert_keys_to_camel_case(item) for item in obj]
    else:
        return obj


def save_to_json(dict_data, file):
    with open(file, 'w') as outfile:
        json.dump(dict_data, outfile, indent=4)


def open_jsons(file):
    with open(file, 'r') as f:
        return json.load(f)


def upload_avantdata(data, template_name, custom={}):
    Template(name=template_name,
             aliases=TEMPLATE_ALIASES,
             template=data,
             custom=custom,
             baseurl=POST_URL,
             append=True).upload()
    UpsertBulk(data=data,
               baseurl=POST_URL).upload()


""" import json
with open('rules.json', 'r') as f:
    file = json.load(f)
    print([l.get('@name') for l in file.get('response').get('result').get('rules').get('entry') if not l.get('log-setting')]) """


class Template:
    """Template
    A class to manage creation of templates
    Args:
        name (str): Name of the template
        template (list(dict) or dict): Dictionary or dictionaries with keys to generate a template
        baseurl (str, optional): Baseurl to execute the upsert bulk 
        api (str, optional): Endpoint where the connection with database is set
        cluster (str, optional): Header parameter for communication with the api
        verifySSL (bool, optional): Bool to verify SSL of requests
        order (int, optional): Order attribute of the template
        shards (int, optional): Shards attribute of the template
        custom (dict, optional): Attributes to not be considered as text
        aliases (str, optional): Aliases attribute of the template
        mappingName (str, optional): Mappings attribute of the template
        templateName (str, optional): Template attribute of the template body
        regenerate (bool, optional): Always create template if True
        append (bool, optional): Append missing keys in the template if True
    Attributes:
        name (str): Name of the template
        template (list(dict) or dict): Dictionary or dictionaries with keys to generate a template
        baseurl (str): Baseurl to execute the upsert bulk 
        api (str): Endpoint where the connection with database is set
        cluster (str): Header parameter for communication with the api
        verifySSL (bool): Bool to verify SSL of requests
        order (int): Order attribute of the template
        shards (int): Shards attribute of the template
        custom (dict): Attributes to not be considered as text
        aliases (str): Aliases attribute of the template
        mappingName (str): Mappings attribute of the template
        templateName (str): Template attribute of the template body
        regenerate (bool): Always create template if True
        append (bool): Append missing keys in the template if True
        data(dict): The generated template
    Example:
        >>> import logging
        >>> logging.basicConfig(level=logging.INFO)
        >>> import avantpy
        >>> dataList = []
        >>> dataList.append({'testing1':'test', 'testing2':'test', 'testing3':'test'})
        >>> dataList.append({'testing4':'test', 'testing5':'test', 'testing6':'test'})
        >>> template = avantpy.upload.Template(template=dataList, name='testing_template', aliases='TestingTemplate', baseurl='https://')
        >>> template.upload()
        INFO:avantpy.upload.Template:Uploading template testing_template
        INFO:avantpy.upload.Template:{"acknowledged":true}
        >>> template.data.get('body').keys()
        dict_keys(['template', 'settings', 'mappings', 'aliases'])
        >>> template.data.get('body').get('mappings').get('testing_template').get('properties').keys()
        dict_keys(['testing1', 'testing3', 'testing6', 'testing2', 'testing4', 'testing5', 'GenerateTime'])
        >>> dataList.append({'testing7':'test', 'testing8':'test', 'testing9':'test'})
        >>> template.upload()
        INFO:avantpy.upload.Template:Template testing_template already exists
        >>> template.upload(append=True)
        INFO:avantpy.upload.Template:Appending keys ['testing7', 'testing8', 'testing9']
        INFO:avantpy.upload.Template:{"acknowledged":true}
        >>> template.data.get('body').get('mappings').get('testing_template').get('properties').keys()
        dict_keys(['testing7', 'testing1', 'testing9', 'testing8', 'testing3', 'testing6', 'testing2', 'testing4', 'testing5', 'GenerateTime']) 
    """

    def __init__(self,
                 name: str,
                 template: Union[List[dict], Tuple[dict], Set[dict], dict],
                 baseurl: Optional[str] = '',
                 api: Optional[str] = '/avantapi/avantData/template',
                 apiCreate: Optional[str] = '/avantapi/avantData/template/create',
                 cluster: Optional[str] = 'AvantData',
                 verifySSL: Optional[str] = False,
                 order: Optional[int] = 1,
                 shards: Optional[int] = 2,
                 custom: Optional[dict] = {},
                 regenerate: Optional[bool] = False,
                 append: Optional[bool] = False,
                 **kwargs: Any):
        self.log = logging.getLogger(__name__)
        self.name = name
        self.template = template
        self.baseurl = self.getUrl(baseurl)
        self.api = api
        self.apiCreate = apiCreate
        self.cluster = cluster
        self.verifySSL = verifySSL
        self.templateName = kwargs.get('templateName', self.name+'*')
        self.mappingName = kwargs.get('mappingName', self.name)
        self.aliases = kwargs.get('aliases', re.sub(
            r'[^a-zA-Z0-9_]*', '', self.name.title()))
        self.order = order
        self.shards = shards
        self.custom = custom
        self.regenerate = regenerate
        self.append = append
        self.data = self.format_template()

    def __repr__(self):
        return 'Generated template:\n{}'.format(json.dumps(self.data, indent=4))

    def properties_map(self, value: Union[dict, str]) -> dict:
        """Maps the provided value to a dictionary representing its properties.
        Args:
            value (Union[dict, str]): The value to map. Can be either a dictionary or a string.
        Returns:
            dict: A dictionary representing the properties of the provided value.
        Example:
            >>> properties_map('int')
            {'type': 'integer'}
        """
        if isinstance(value, dict):
            return value
        valuesMap = {
            "date": {
                "type": "date",
                "format": "yyyy/MM/dd HH:mm:ss||epoch_millis"
            },
            "int": {
                "type": "integer"
            },
        }
        if valuesMap.get(value):
            return valuesMap[value]
        return {"type": value}

    def get_template_dict(self, template: Union[List[dict], Tuple[dict], Set[dict], dict]) -> dict:
        """Returns a dictionary containing all keys and values present in the input template.
        Args:
            template: A template dictionary or a list, tuple or set of dictionaries.

        Returns:
            A dictionary containing all keys and values present in the input template.
        """
        if isinstance(template, (list, tuple, set)):
            allKeys = {k for d in template for k in d.keys()}
            templateDict = dict()
            for key in allKeys:
                for di in template:
                    if di.get(key):
                        if isinstance(di.get(key), dict):
                            if not templateDict.get(key):
                                templateDict[key] = dict()
                            templateDict[key].update(di.get(key))
                        else:
                            templateDict[key] = di.get(key)
                            break
        elif isinstance(template, dict):
            templateDict = template
        return templateDict

    def generate_properties(self, template, gtime=True):
        """Returns a dictionary containing the properties of the input template.
        Args:
            template: A template dictionary or a list, tuple or set of dictionaries.
            gtime: A boolean flag that indicates whether or not to generate the "GenerateTime" property.
                Default is True.

        Returns:
            A dictionary containing the properties of the input template.
        """
        newDict = dict()
        textType = {
            "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    },
            "analyzer": "WS"
        }
        templateDict = self.get_template_dict(template)
        for k, v in templateDict.items():
            if k in self.custom.keys():
                newDict[k] = self.properties_map(self.custom[k])
            elif isinstance(v, dict):
                newDict[k] = {
                    "properties": self.generate_properties(v, gtime=False)}
            elif isinstance(v, (list, tuple, set)):
                if all([isinstance(d, dict) for d in v]):
                    newDict[k] = {"type": "object"}
                else:
                    newDict[k] = textType
            else:
                newDict[k] = textType
        if not newDict.get('GenerateTime') and gtime:
            newDict["GenerateTime"] = {
                "type": "date",
                "format": "yyyy/MM/dd HH:mm:ss||epoch_millis"
            }
        return newDict

    def format_template(self):
        """Generate the complete template"""
        if isinstance(self.template, (list, tuple, set, dict)):
            properties = self.generate_properties(self.template)
        else:
            raise ValueError('Template needs to be a dict, list, tuple or set')
        formattedTemplate = {
            "name": self.name,
            "order": self.order,
            "body": {
                "template": self.templateName,
                "settings": {
                    "index": {
                        "refresh_interval": "5s",
                        "analysis": {
                            "analyzer": {
                                "WS": {
                                    "filter": [
                                        "lowercase"
                                    ],
                                    "type": "custom",
                                    "tokenizer": "whitespace"
                                }
                            }
                        },
                        "number_of_shards": self.shards,
                        "number_of_replicas": "0"
                    }
                },
                "mappings": {
                    self.mappingName: {
                        "_all": {
                            "norms": False,
                            "enabled": True
                        },
                        "_size": {
                            "enabled": True
                        },
                        "properties": properties
                    }
                },
                "aliases": {
                    self.aliases: {}
                }
            }
        }
        return formattedTemplate

    def upload(self, **kwargs):
        """Upload a new Elasticsearch template or append to an existing one.
        Args:
            regenerate (bool, optional): If True, the existing template will be deleted and a new one with the same name will be created. Defaults to self.regenerate.
            append (bool, optional): If True, new properties in the template will be added to the existing template. Defaults to self.append.
        Raises:
            Exception: If the upload fails.
        """
        regenerate = kwargs.get('regenerate', self.regenerate)
        append = kwargs.get('append', self.append)
        if self.data:
            headers = {
                'cluster': self.cluster
            }
            response = requests.get(url=self.baseurl+self.api+'/'+self.name,
                                    headers=headers,
                                    verify=self.verifySSL
                                    )
            if response.status_code == 404 or regenerate:
                self.log.info('Uploading template {}'.format(self.name))
                responseCreate = requests.post(url=self.baseurl+self.apiCreate,
                                               headers=headers,
                                               data=json.dumps(self.data),
                                               verify=self.verifySSL)
                self.log.info(responseCreate.text)
            elif append:
                rJson = response.json()
                tmps = rJson.get(next(iter(rJson)))
                changed = False
                appendedKeys = []
                for k, v in tmps.get('mappings').items():
                    properties = v.get('properties')
                    newTemplate = self.get_template_dict(self.template)
                    appendKeys = set(newTemplate.keys())-set(properties.keys())
                    appendedKeys.extend(list(appendKeys))
                    if appendKeys:
                        changed = True
                        appendTemplate = {newK: newTemplate.get(
                            newK) for newK in appendKeys}
                        appendProperties = self.generate_properties(
                            appendTemplate, gtime=False)
                        properties.update(appendProperties)
                        rJson[next(iter(rJson))
                              ]['mappings'][k]['properties'] = properties
                self.data = {
                    "name": self.name,
                    "order": tmps.pop('order'),
                    "body": rJson.get(next(iter(rJson)))
                }
                if changed:
                    self.log.info('Appending keys {}'.format(appendedKeys))
                    responseCreate = requests.post(url=self.baseurl+self.apiCreate,
                                                   headers=headers,
                                                   data=json.dumps(self.data),
                                                   verify=self.verifySSL)
                    self.log.info(responseCreate.text)
                else:
                    self.log.info(
                        'Nothing to append in template {}'.format(self.name))
            else:
                self.log.info('Template {} already exists'.format(self.name))

    def getUrl(self, url: str) -> str:
        """This function returns a URL string.

        If the `url` argument is not empty, the function simply returns it.

        If the `url` argument is empty, the function creates a UDP socket and connects to the IP address and port
        of Google's public DNS server (8.8.8.8 on port 80) to get the IP address of the host. It then formats the IP
        address as a string and returns it with the `https://` protocol prefix.

        Args:
            url: string representing the URL that the function will try to retrieve.

        Returns:
            str: The URL to use for API requests.
        """
        if not url:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            host_ip = s.getsockname()[0]
            s.close()
            return 'https://{}'.format(host_ip)
        return url


class UpsertBulk:
    """Bulk Uploader
    A class to manage bulk uploads of data
    Args:
        data (list(dict)): List of dictionaries to be indexed [{"id":..., "index":..., "type":..., ...},...]
        baseurl (str, optional): Baseurl to execute the upsert bulk 
        api (str, optional): Endpoint where the connection with database is set
        cluster (str, optional): Header parameter for communication with the api
        verifySSL (bool, optional): Bool to verify SSL of requests
        chunkSize (int, optional): Number of documents to send in each bulk requests
        threads (int, optional): Number of threads to send each chunk of documents
        url (str, optional): Default to join the url path with api path
    Attributes:
        data (list(dict)): List of dictionaries to be indexed [{"id":..., "index":..., "type":..., ...},...]
        updated (int): Number of documents successfully updated
        created (int): Number of documents successfully created
        failed (int): Number of documents that failed indexing
        errors (dict): Dict subclass for counting hashable objects from collections (Counter)
        log (logger): Logger with __name__
        baseurl (str): Baseurl to execute the upsert bulk 
        api (str): Endpoint where the connection with database is set
        cluster (str): Header parameter for communication with the api
        verifySSL (bool): Bool to verify SSL of requests
        chunkSize (int): Number of documents to send in each bulk requests
        threads (int): Number of threads to send each chunk of documents
        url (str): Default to join the url path with api path
    Example:
        >>> import logging
        >>> logging.basicConfig(level=logging.INFO)
        >>> import avantpy
        >>> dataList = []
        >>> dataList.append({'id':'6fee099da7dfbb67599d7fa7389de898', 'type':'test', 'index':'test', 'testKey': 'firstValue'})
        >>> dataList.append({'id':'58f77dcc14a41b2984e298e86db85c73', 'type':'test', 'index':'test', 'testKey': 'secondValue'})
        >>> dataList.append({'id':'ed23fa12819a63198b5c0b171ebbbf2d', 'type':'test', 'index':'test', 'testKey': 'thirdValue'})
        >>> avantpy.upload.UpsertBulk(dataList, baseurl='https://')
        INFO:avantpy.upload.UpsertBulk:Total: 3
        INFO:avantpy.upload.UpsertBulk:Updated: 0, Created: 3. 
        INFO:avantpy.upload.UpsertBulk:3 successfully executed with 0 failures
        INFO:avantpy.upload.UpsertBulk: Created: 3 / Updated: 0 / Failed: 0
    """

    def __init__(self,
                 data: Union[List[dict], Tuple[dict], Set[dict]],
                 baseurl: Optional[str] = '',
                 api: Optional[str] = '/avantapi/avantData/index/bulk/general/upsert',
                 cluster: Optional[str] = 'AvantData',
                 verifySSL: Optional[bool] = False,
                 chunkSize: Optional[int] = 1000,
                 threads: Optional[int] = 1,
                 **kwargs: Any):
        self.log = logging.getLogger(__name__)
        self.baseurl = self.getUrl(baseurl)
        self.api = api
        self.cluster = cluster
        self.verifySSL = verifySSL
        self.chunkSize = chunkSize
        self.threads = threads
        self.data = data
        self.url = kwargs.get('url', self.baseurl+self.api)
        self.updated, self.created, self.failed = (0, 0, 0)
        self.errors = Counter()

    def __repr__(self):
        return '{} documents ready to be uploaded to {}. Use upload() method to upload'.format(len(self.data), self.baseurl)

    def chunkSend(self, chunk: Union[List[dict], Tuple[dict], Set[dict]]):
        """Sends a chunk of data to be indexed into the Elasticsearch cluster.
        Args:
            chunk (list(dict) or tuple(dict) or set(dict)): A list of dictionaries to be indexed.
        The function sends a chunk of data to be indexed into the Elasticsearch cluster by making a PUT request
        to the Elasticsearch server. The data is sent as a JSON object in the request body, and the 'cluster' header 
        is set to the cluster name provided during object instantiation.
        The function then processes the response returned from the Elasticsearch server. It updates the 'updated'
        and 'created' counters based on the number of documents that were updated and created, respectively. If there
        were any errors during indexing, the function updates the 'errors' dictionary with the count of errors
        encountered, along with the reason for each error.
        """
        jsonToSend = {'body': json.loads(json.dumps(chunk))}
        headers = {'cluster': self.cluster}
        responseBulk = requests.put(url=self.url,
                                    headers=headers,
                                    data=json.dumps(jsonToSend),
                                    verify=self.verifySSL)
        try:
            responseJson = json.loads(responseBulk.text)
            if responseJson.get('items'):
                results = Counter(item.get('update').get('result')
                                  for item in responseJson.get('items'))
                self.updated += results.get('updated', 0)
                self.created += results.get('created', 0)
                if responseJson.get('errors'):
                    self.errors.update(Counter(item.get('update').get('error').get(
                        'reason') for item in responseJson.get('items') if item.get('update').get('error')))
                self.log.info('Updated: {}, Created: {}. '.format(
                    self.updated, self.created))
        except Exception as e:
            self.log.warning(responseBulk.text)
            self.log.error(e)

    def upload(self):
        """This function uploads data in chunks and returns a status message.

        If the `data` attribute of the object is not empty, the function logs the total number of items in the `data`
        list, and splits the list into chunks (of size `chunkSize`) for concurrent processing using threads (number of
        threads is `threads`).

        If `threads` is greater than 1, the function uses `concurrent.futures.ThreadPoolExecutor` to execute the
        `chunkSend` method on the chunks concurrently. If `threads` is 1 or less, the function executes the `chunkSend`
        method on each chunk sequentially.

        If there were any errors during execution, the function logs the reasons for the failures along with the number
        of items that failed.

        The function logs the number of items that were created and updated successfully, as well as the number of items
        that failed.

        Returns:
            A string representing the status of the upload operation. The string logs the total number of items in the `data`
        list, the number of items that were created and updated successfully, as well as the number of items that failed.
        """
        if self.data:
            self.log.info('Total: {}'.format(len(self.data)))
            chunks = [self.data]
            if len(self.data) > self.chunkSize:
                chunks = [self.data[x:x+self.chunkSize]
                          for x in range(0, len(self.data), self.chunkSize)]
            if self.threads > 1:
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
                    executor.map(self.chunkSend, chunks)
            else:
                for chunk in chunks:
                    self.chunkSend(chunk)
            if self.errors:
                self.failed += sum(self.errors.values())
                for k, v in self.errors.items():
                    self.log.warning('{} failed. Reason: {}'.format(v, k))
            self.log.info('{} successfully executed with {} failures'.format(
                self.updated+self.created, self.failed))
            self.log.info(
                'Created: {} / Updated: {} / Failed: {}'.format(self.created, self.updated, self.failed))
        else:
            self.log.info('Empty list')

    def getUrl(self, url: str) -> str:
        """This function returns a URL string.

        If the `url` argument is not empty, the function simply returns it.

        If the `url` argument is empty, the function creates a UDP socket and connects to the IP address and port
        of Google's public DNS server (8.8.8.8 on port 80) to get the IP address of the host. It then formats the IP
        address as a string and returns it with the `https://` protocol prefix.

        Args:
            url: string representing the URL that the function will try to retrieve.

        Returns:
            str: The URL to use for API requests.
        """
        if not url:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            host_ip = s.getsockname()[0]
            s.close()
            return 'https://{}'.format(host_ip)
        return url


if __name__ == '__main__':
    script()
