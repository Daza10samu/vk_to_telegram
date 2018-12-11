#! /usr/bin/python3

import os, configparser, argparse

'''
    pass
'''

__author__ = 'EtFortuitiCasusGignitMundoSuccedunt'

pwd = os.popen('pwd').readline()[:-1]

def dialog():
    pass
    exit()

def makecfg():
    config = configparser.ConfigParser()
    bot_token = input('What is token in your telegram bot:')
    user_ids = str(input('Your telegram accounts:').split())
    vk_users = '[]'
    if user_ids=='[]' or bot_token=='':
        raise Exception('Token or ids must be not zero')
    config.add_section('General')
    config.set('General', 'bot_token', bot_token)
    config.set('General', 'user_ids', user_ids)
    with open(pwd+'/.config', 'w') as f:
        config.write(f)
    print('Config have been made. Now add the users')
    exit()

def args():
    parser = argparse.ArgumentParser(description='Make config for vk_to_telegram')
    parser.add_argument('-r', '--remake', help='Regenerate config file', action='store_true')
    return parser.parse_args()

arg = args()
if arg.remake:
    makecfg()

if '.config' in os.listdir(pwd):
    dialog()

makecfg()