#! /usr/bin/python3

import os, configparser, telebot
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api, datetime, threading, re

pwd = os.environ['HOME']+'/.config/vk_to_telegram'
config = configparser.ConfigParser()
config.read(pwd+'/config')
bot_token = config.get('General', 'bot_token')
send_ids = config.get('General', 'user_ids')
send_ids = [x.strip("[] '") for x in send_ids.split(',')]
bot = telebot.TeleBot(bot_token)

def bot_send(msg):
    for i in send_ids:
        bot.send_message(i, msg)

def ParseAtta(msg):
    for i in msg['attachments']:
        print(i)
        print()
        attachments = []
        if i['type'] == 'sticker':
            sticker = i['sticker']
            print(sticker)
            print()
            maxq = 0
            for j in sticker['images']:
                if j['width']*j['height']>maxq:
                    maxq = j['width']*j['height']
                    url = j['url']
            attachments.append('sticker {}'.format(url))
        elif i['type'] == 'photo':
            maxq = 0
            for j in i['photo']['sizes']:
                if j['width']*j['height']>maxq:
                    maxq = j['width']*j['height']
                    url = j['url']
            attachments.append('photo {}'.format(url))
        elif i['type'] == 'audio_message':
            attachments.append('voice message '+i['audio_message']['link_ogg'])
        else:
            attachments.append(str(i))
    return attachments

def ParseForw(msg, api, fwd_level=1):
    bot_send('| '*(fwd_level-1)+'\\_'+'\tForwards: ')
    for i in msg['fwd_messages']:
        print(i)
        print()
        print()
        user = api.users.get(user_ids=i['from_id'])[0]
        bot_send('| '*fwd_level+'from "{} {}": '.format(user['first_name'], user['last_name']) + i['text'])
        if 'attachments' in i.keys():
            if i['attachments']!=[]:
                attachments = ParseAtta(i)
                bot_send('|'*fwd_level+'\tattachments: '+attachments[0])
                for i in attachments[1:]:
                    bot_send(i)
        if 'fwd_messages' in i.keys():
            if msg['fwd_messages']!=[]:
                ParseForw(i, me, api, fwd_level+1)
        print()
        print()

def ParsePriv(msg, me, user, api):
    print(msg)
    print()
    print()
    user = api.users.get(user_ids=msg['from_id'])[0]
    bot_send('Sent from "{} {}" message to "{} {}": '.format(user['first_name'], user['last_name'], me['first_name'], me['last_name']) + msg['text'])
    if msg['attachments']!=[]:
        attachments = ParseAtta(msg)
        bot_send('Attachments: '+attachments[0])
        for i in attachments[1:]:
            bot_send(i)
    if 'fwd_messages' in msg.keys():
        if msg['fwd_messages']!=[]:
            ParseForw(msg, api)
    print()
    print()

def ParseChat(msg, me, user, api):
    chat = api.messages.getChat(chat_id=msg['peer_id']-2000000000)
    print(msg, chat)
    print()
    print()
    bot_send('In chat "{}" sent from "{} {}" message to "{} {}": '.format(chat['title'], user['first_name'], user['last_name'], me['first_name'], me['last_name']) + msg['text'])
    if msg['attachments']!=[]:
        attachments = ParseAtta(msg)
        bot_send('Attachments: '+attachments[0])
        for i in attachments[1:]:
            bot_send(i)
    if msg['fwd_messages']!=[]:
        ParseForw(msg)
    print()
    print()

class LongPool(threading.Thread):

    def __init__(self, account):
        threading.Thread.__init__(self)
        self.paused = False
        self.token = account[0]
        self.chat_users = account[1]
        self.chats = account[2]

    def run(self):
        session = vk_api.VkApi(token=self.token, api_version='5.92')
        api = session.get_api()
        me = api.users.get()[0]
        while 1:
            long_pooll = VkLongPoll(session)
            try:
                for i in long_pooll.listen():
                    if self.paused:
                        continue
                    if i.type == VkEventType.MESSAGE_NEW:
                        msg_ext = api.messages.getById(message_ids=i.message_id, extended = 1)
                        msg = msg_ext['items'][0]
                        user = msg_ext['profiles'][0]
                        if msg['out']:
                            continue
                        if msg['peer_id']-2000000000 in self.chats:
                           ParseChat(msg, me, user, api)
                        elif msg['from_id'] in self.chat_users:
                            ParsePriv(msg, me, user, api)

            except Exception as exep:
                bot_send('Ohhh... there are some errors: '+str(exep))

    def stop(self):
        self.paused = True

    def resume(self):
        self.paused = False

@bot.message_handler(commands=['start'])
def handle_start(message):
    for i in threads:
        i.resume()
    for i in send_ids:
        bot.send_message(i, 'Bot have resumed')

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    for i in threads:
        i.stop()
    for i in send_ids:
        bot.send_message(i, 'Bot have stoped')
@bot.message_handler(commands=['kill'])
def kill(message):
    for i in send_ids:
        bot.send_message(i, 'Bot have been killed')
    *proc, = os.popen('ps axu | grep resender')
    pid = proc[0].split()[1]
    os.system('kill '+pid)

accounts = [i.strip("[]' ") for i in config.get('General', 'vk_users').split(',')]
check_configs = []
for name in accounts:
    check_configs.append([config.get(name, 'token'), [int(i.strip("[] '")) for i in config.get(name, 'chat_users').split(',')], [int(i.strip("[] '")) for i in config.get(name, 'chats').split(',')]])

global threads
threads = []
for i in check_configs:
    threads.append(LongPool(i))
    threads[-1].start()

while 1:
    try:
        bot.polling(none_stop=True)
    except KeyboardInterrupt:
        exit()
    except Exception as exep:
        bot_send('Ohhh... there are some errors: '+str(exep))
