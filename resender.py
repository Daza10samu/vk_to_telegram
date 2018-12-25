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


'''
{'attachments': [], 'random_id': 0, 'peer_id': 2000000014, 'from_id': 389608140, 'fwd_messages': [{'text': '', 'id': 103765, 'from_id': 26802336, 'fwd_messages': [{'text': 'Н Х', 'id': 103753
, 'from_id': 317111470, 'conversation_message_id': 19337, 'update_time': 0, 'peer_id': 2000000014, 'date': 1545726097, 'attachments': []}, {'text': 'И У', 'id': 103755, 'from_id': 64075685, '
conversation_message_id': 19339, 'update_time': 0, 'peer_id': 2000000014, 'date': 1545726098, 'attachments': []}, {'text': 'К Я', 'id': 103757, 'from_id': 187123658, 'conversation_message_id'
: 19341, 'update_time': 0, 'peer_id': 2000000014, 'date': 1545726108, 'attachments': []}, {'text': 'И С', 'id': 103759, 'from_id': 188320403, 'conversation_message_id': 19343, 'update_time': 
0, 'peer_id': 2000000014, 'date': 1545726124, 'attachments': []}, {'text': 'Т О', 'id': 103760, 'from_id': 26802336, 'conversation_message_id': 19344, 'update_time': 0, 'peer_id': 2000000014,
 'date': 1545726131, 'attachments': []}, {'text': 'А С', 'id': 103761, 'from_id': 317111470, 'conversation_message_id': 19345, 'update_time': 0, 'peer_id': 2000000014, 'date': 1545726138, 'at
tachments': []}], 'conversation_message_id': 19349, 'update_time': 0, 'peer_id': 2000000014, 'date': 1545726169, 'attachments': []}], 'out': 0, 'date': 1545736468, 'text': 'Это шо, роккебол?'
, 'id': 103784, 'conversation_message_id': 19367, 'is_hidden': False, 'important': False} {'id': 14, 'title': '10д', 'admin_id': 22858128, 'users': [22858128, 160589921, 187123658, 151777744,
 344477715, 195211020, 64075685, 181184918, 120722492, 196883595, 110640021, 234534617, 26802336, 389608140, 143920317, 410192331, 317111470, 244904389, 269502954, 190903868, 243121011, 21881
4281, 164572412, 341299001, 239345159, 309690797, 138038606, 161896672, 188320403, 190870897, 205414825, 465203592], 'members_count': 32, 'push_settings': {'disabled_until': -1, 'sound': 1}, 
'type': 'chat'}
'''