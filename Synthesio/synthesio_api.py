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
               'client_id': '', 'client_secret': '',  #need client_id & client_secret
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
    get_research_dashboard = [item for item in all_dashboards if item == ''] #need item id
    if get_research_dashboard:
        research_report_id = '' #need research_report_id
        return research_report_id
    else:
        print('Oops! This isn\'t the Research dashboard.')
        
def format_query(raw_query):
    get_tokens = nltk.word_tokenize(raw_query)
    if len(get_tokens) == 1:
        single_word = ' '.join(get_tokens)
        return single_word
    else:
        get_booleans = [word for word in get_tokens if word == 'and']
        format_tokens = ['"{0}"'.format(word) for word in get_tokens if word != get_tokens[0] and word != 'and']
        format_tokens.insert(0, get_tokens[0])
        for place, word in enumerate(get_booleans):
            format_tokens.insert(2*place+1, word)
        make_string = ' '.join(format_tokens)
        make_string_upper = make_string.replace('and', 'AND')
        return make_string_upper
        
def get_mentions_query_single(words, research_report_id, size, access_token):
    formatted_query = format_query(words)
    payload = {'filters': {'query': formatted_query}}
    mentions_query_single = post_requests_data_json('mention/v2/reports/' + research_report_id + '/_search?size=' + size, headers_json, payload, access_token)
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
    with open(title + '.csv', 'w') as makecsvfile:
        labels = [key for key in ordered_master_dict.keys()]
        data = csv.writer(makecsvfile, delimiter=',',
                          quotechar='|', quoting=csv.QUOTE_MINIMAL)
        data.writerow(labels)
        [data.writerow(row) for row in get_values(csv_content)]

def main():
    username = input('What is your username? ')
    password = input('What is your password? ')
    access_token = get_token(username, password)
    all_dashboard_ids = get_dashboards(access_token)
    research_report_id = get_research_report_id(all_dashboard_ids)
    query_by_word = input('What word(s) would you like to search for? Example: Illinois and wifi ')
    query_size = input('How many results would you like? Please supply a number: ')
    single_query = get_mentions_query_single(query_by_word, research_report_id, str(query_size), access_token)
    normalize(single_query)
    print_file('query_result', single_query)
    print('Your results have downloaded successfully.')

#main call
main()
