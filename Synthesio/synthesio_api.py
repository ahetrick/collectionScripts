'''
Created on September 2, 2017
@author: ahetrick
'''

#import libraries
from __future__ import unicode_literals
import json
import requests
import csv
from collections import OrderedDict
import nltk
import re

#parameters & variables
url_start = 'https://rest.synthesio.com/'
headers_start = 'Content-Type'
headers_json = 'application/json'
headers_xform = 'application/x-www-form-urlencoded'
auth = 'Authorization'
bear = 'Bearer '

master_dict = {'author_id': 1, 'channel': 1, 'collaboration_status': 1, 'collaboration_user': 1, 'content': 1, 'copyright': 1, 'crawled_at': 1, 'date': 1,
               'deleted': 1, 'extra_properties': 1, 'human_review_status': 1, 'id': 1, 'influence': 1, 'infused_at': 1,'interactions': 1,
               'language': 1, 'license': 1, 'location': 1, 'meta': 1, 'metric_list': 1, 'native_id': 1, 'parent_id': 1,
               'review': 1, 'root_id': 1, 'sentiment': 1, 'site_id': 1, 'source_id': 1, 'synthesio_rank': 1, 'tags': 1, 'title': 1, 
               'twitter': 1, 'type':1, 'url': 1}

ordered_master_dict = OrderedDict(sorted(master_dict.items()))

#methods 
def post_requests_data(url_end, headers_end, payload):
    url = url_start + url_end
    headers = {headers_start: headers_end} 
    resource = requests.post(url, data=payload, headers=headers)
    if resource:
        json_resource = resource.json()
        return json_resource
    else:
        print(resource.status_code)
        
def post_requests_data_json(url_end, headers_end, payload, access_token):
    url = url_start + url_end
    headers = {headers_start: headers_end, auth: bear + access_token} 
    resource = requests.post(url, json=payload, headers=headers)
    if resource:
        json_resource = resource.json()
        return json_resource
    else:
        print(resource.status_code)

def get_requests_no_data(url_end, access_token):
    url = url_start + url_end
    headers = {auth: bear + access_token} 
    resource = requests.get(url, headers=headers)
    if resource:
        json_resource = resource.json()
        return json_resource
    else:
        print(resource.status_code)  

def get_token(input_username, input_password):
    payload = {'grant_type': 'password', 'username': input_username, 'password': input_password, 
               'client_id': '',
               'client_secret': '',  #need client_id & client_secret
               'scope': 'read'}
    json_token = post_requests_data('security/v1/oauth/token/', headers_xform, payload)
    token = json_token['access_token']
    return token

def get_dashboards(access_token):
    json_dashboards = get_requests_no_data('workspace/v1/dashboards?', access_token)
    data_list = json_dashboards['data']
    dashboards = [item['id'] for item in data_list]
    return dashboards

def get_research_report_id(all_dashboards):
    get_research_dashboard = [item for item in all_dashboards if item == '254048'] #need item id
    if get_research_dashboard:
        research_report_id = '264950' #need research_report_id
        return research_report_id
    else:
        print('Oops! This isn\'t the Research dashboard.')
        

def format_query(raw_query):
    
    # seperate exact on “and” and "not"
    regex = re.compile(r'\band\b|\bnot\b',re.IGNORECASE)
    keywords = regex.split(raw_query)
    boolean = regex.findall(raw_query)
    
    new_keywords = []
    
    # check if there's or in new keywords
    for k in keywords:
        or_regex = re.compile(r'\bor\b',re.IGNORECASE)
        or_keywords = or_regex.split(k)
        or_boolean = or_regex.findall(k)
        
        or_new_keywords = []
        for kk in or_keywords:
            or_new_keywords.append(" ".join(kk.split()))
    
        # if there's "or" boolean exist
        # construct "or" boolean first
        if or_boolean != []:
            if '' in or_new_keywords:
                print('illegal query! Please double check!')
                return None
            else:
                sub_query_string = ""
                for i in range(len(or_new_keywords)):
                    if i== 0:
                        sub_query_string += "(\"" + or_new_keywords[i] + "\" " + or_boolean[i].upper() + " "
                    elif i== len(or_new_keywords)-1:
                        sub_query_string += "\"" + or_new_keywords[i] + "\")"
                    else:
                        sub_query_string += "\"" + or_new_keywords[i]  + "\" " + or_boolean[i].upper() + " "

            new_keywords.append(sub_query_string)
        
        # if "or" boolean not exist
        # just strip the trailing spaces and wrap them into " "
        else:
            new_keywords.append("\"" +  " ".join(k.split()) + "\"")
                 
    if '\"\"' in new_keywords:
        print('illegal query! Please double check!')
        return None
    
    else:
        
        new_query_string = ""
        for i in range(len(new_keywords)):
            if i == len(new_keywords)-1:
                new_query_string += new_keywords[i] 
            else:
                new_query_string += new_keywords[i]  + " " + boolean[i].upper() + " "
        
        return new_query_string


    
        
def get_mentions_query_single(words, research_report_id, size, access_token):
    formatted_query = format_query(words)
    payload = {'filters': {'query': formatted_query}}
    mentions_query_single = post_requests_data_json('mention/v2/reports/' + research_report_id + '/_search?size=' + size + '&sort=desc', headers_json, payload, access_token)
    mentions_query_single_data = mentions_query_single['data']
    return mentions_query_single_data

def normalize(check_query):
    i = 0 
    while i < len(check_query):
        if check_query[i].keys() != master_dict.keys():
            check_query[i].update(dict.fromkeys(set(master_dict).difference(check_query[i]), 'None'))
            i+=1

def get_values(keys_values): 
    values = []
    i = 0
    while i < len(keys_values):
        ordered_dic_keys_values = OrderedDict(sorted(keys_values[i].items()))
        str_values_in_dic = [str(value) for key, value in ordered_dic_keys_values.items()]
        replaced_values = [item.replace(',',' ') for item in str_values_in_dic]
        values.append(replaced_values)
        i+=1
    return values
        
def print_file(title, content):
    csv_title = title
    csv_content = content
    with open(title + '.csv', 'w',newline="") as makecsvfile:
        labels = [key for key in ordered_master_dict.keys()]
        data = csv.writer(makecsvfile, delimiter=',',
                          quotechar='|', quoting=csv.QUOTE_MINIMAL)
        data.writerow(labels)
        for row in get_values(csv_content):
            try:
                [data.writerow(row) ]
            except:
                print('encoding error ignored!')

if __name__ == '__main__':

    username = input('What is your username? ')
    print('\n')
    password = input('What is your password? ')
    print('\n')
    access_token = get_token(username, password)
    research_report_id = get_research_report_id(get_dashboards(access_token))

    while True:
        query_by_word = input('What word(s) would you like to search for?\nAND, OR, NOT boolean are available.\ne.g.Illinois or Indiana and wifi and internet not computer\n')
        print('\n')
        query_size = input('How many results would you like? Please supply a number: ')
        print('\n')
        if format_query(query_by_word) != None:
            confirm = input('Does this look right to you: ' + format_query(query_by_word) + '\nreply Y/N: ')
            print('\n')
            if confirm == 'Y' or confirm == 'y':
                single_query = get_mentions_query_single(query_by_word, research_report_id, str(query_size), access_token)
                normalize(single_query)
                title = input('Please input the filename you\'d like to save (.csv): ')
                print('\n')
                print_file(title, single_query)
                print('Your results have downloaded successfully.')
                break
