#! /usr/bin/python3

import requests, argparse, re, getpass

'''
    This script was maden to get vk_token
'''

__author__ = 'EtFortuitiCasusGignitMundoSuccedunt'

def scope_finder(inp, scopes):
    s = 0

    if inp.a:
        s = 140491999


    elif len(inp.s)>0:
        for i in inp.s:
            try:
                s += scopes[i]
            except Exception as e:
                raise Exception('Incorrect scope: '+i)

    if len(inp.s)==0:
        raise Exception('There are no scope. Use -l key to list scopes')

    return s

def args():
    parser = argparse.ArgumentParser(description='Get token to use vk_api')
    parser.add_argument('-s', type=str, help='Scopes( capabilities) for vk_api. To make unlimitet token ose offline\nExample: vk_token_get -s offline notify\n', nargs='+', default = [])
    parser.add_argument('-p', type=str, help='identficator of device( available:android, ios; default:android)\nExample: vk_token_get -p android\n', default = 'android')
    parser.add_argument('-a', help='use to enable all scopes', action='store_true')
    parser.add_argument('-l', help='list available scopes', action='store_true')

    return parser.parse_args()

scopes = {
    'notify' : 1,
    'friends' : 2,
    'photos' : 4,
    'audio' : 8,
    'video' : 16,
    'stories' : 64,
    'pages' : 128,
    'status' : 1024,
    'notes' : 2048,
    'messages' : 4096,
    'wall' : 8192,
    'ads' : 32768,
    'offline' : 65536,
    'docs' : 131072,
    'groups' : 262144,
    'notifications' : 524288,
    'stats' : 1048576,
    'email' : 4194304,
    'market' : 134217728
}

platforms = {
    'android' : ['2274003', 'hHbZxrka2uZ6jB1inYsH'],
    'ios' : ['3140623', 'VeWdmVclDCtn6ihuP1nt']
}

inp = args()

if inp.l:
    print(', '.join(scopes.keys()))
    exit()

scope = scope_finder(inp, scopes)
platform = platforms[inp.p]
login = input('Login:')
passwd = getpass.getpass()

token_page = requests.get('https://oauth.vk.com/token?grant_type=password&scope={}&client_id={}&client_secret={}&username={}&password={}'.format(scope, platform[0], platform[1], login, passwd))
token = re.findall(r'"access_token":"([^"]*)"', token_page.text)
if token==[]:
    raise Exception('Wrong login/password')

print(token[0])
