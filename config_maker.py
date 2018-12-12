#! /usr/bin/python3

import os, configparser, argparse

'''
    This scrip will make or remove config. To modify config you should find it in $HOME/.config/vk_to_telegram. Then mannually change config
'''

__author__ = 'EtFortuitiCasusGignitMundoSuccedunt'

pwd = os.environ['HOME']+'/.config'
if 'vk_to_telegram' not in os.listdir(pwd):
    os.popen('mkdir '+pwd+'/vk_to_telegram')
pwd = pwd+'/vk_to_telegram'

def CreateAccount(config, accounts):
    name = input('Account name: ')
    token = input('Token: ')
    chat_users = str([int(x) for x in input('Messages from wich users will be resend(IDs, Example: 00000 000001): ').split()])
    chats = str([int(x) for x in input('Messages from wich chats will be resend(IDs, Example: 1 2 23): ').split()])
    accounts = str(accounts + [name])
    config.set('General', 'vk_users', accounts)
    config.add_section(name)
    config.set(name, 'token', token)
    config.set(name, 'chat_users', chat_users)
    config.set(name, 'chats', chats)

def RemoveAccount(config, accounts):
    name = input('Which account do you like to remove: ')
    if name not in accounts:
        raise Exception('Wrong account')
    del accounts[accounts.index(name)]
    config.remove_section(name)
    config.set('General', 'vk_users', str(accounts))


def dialog():
    config = configparser.ConfigParser()
    config.read(pwd+'/config')
    accounts = [i.strip("[]',") for i in config.get('General', 'vk_users').split()]
    if accounts==['']:
        CreateAccount(config, [])
    else:
        print('Accounts vk:', *accounts)
        action = input('Choose your action( remove account(r), add account(a)): ')
        if action=='r':
            RemoveAccount(config, accounts)
        elif action=='a':
            CreateAccount(config, accounts)
        else:
            raise Exception('Incorrect action')
    with open(pwd+'/config', 'w') as f:
        config.write(f)
    print('Config have been updated.')
    exit()


def makecfg():
    config = configparser.ConfigParser()
    bot_token = input('What is token in your telegram bot: ')
    user_ids = str([int(x) for x in input('Your telegram accounts: ').split()])
    vk_users = '[]'
    if user_ids=='[]' or bot_token=='':
        raise Exception('Token or ids must be not zero')
    config.add_section('General')
    config.set('General', 'bot_token', bot_token)
    config.set('General', 'user_ids', user_ids)
    config.set('General', 'vk_users', vk_users)
    with open(pwd+'/config', 'w') as f:
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

if 'config' in os.listdir(pwd):
    dialog()

makecfg()