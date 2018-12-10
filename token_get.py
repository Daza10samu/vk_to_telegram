#! /usr/bin/python3

import requests, argparse, re

def scope_finder(inp, scopes):
    s = 0

    if inp.a:
        s = 140491999


    elif len(inp.s)>0:
        for i in inp.s:
            s += scopes[i]

    else:
        print('Введите значение возможностей -s .../ -a')
        exit()

    return s

def args():
    parser = argparse.ArgumentParser()
    parser.add_argument('login', type=str, nargs='?')
    parser.add_argument('passwd', type=str, nargs='?')
    parser.add_argument('-s', type=str, nargs='+', default = [])
    parser.add_argument('-p', type=str, default = 'android')
    parser.add_argument('-a', action='store_true')
    parser.add_argument('-l', action='store_true')

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

token_page = requests.get('https://oauth.vk.com/token?grant_type=password&scope={}&client_id={}&client_secret={}&username={}&password={}'.format(scope, platform[0], platform[1], inp.login, inp.passwd))

print(re.findall(r'"access_token":"([^"]*)"', token_page.text)[0])