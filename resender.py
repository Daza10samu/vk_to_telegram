#! /usr/bin/python3

import os, configparser, telebot
from vk_api.longpoll import VkLongPoll, VkEventType
from threading import Thread
import vk_api, datetime

pwd = os.environ['HOME']+'/.config/vk_to_telegram'
config = configparser.ConfigParser()
config.read(pwd+'/config')
bot_token = config.get('General', 'bot_token')
send_ids = config.get('General', 'user_ids')
bot = telebot.TeleBot(bot_token)

def bot_send(msg):
    for i in send_ids:
        bot.send_message(i, msg)

class LongPool(Thread):

    def __init__(self, account):
        Thread.__init__(self)
        self.token = account[0]
        self.chat_users = account[1]
        self.chats = account[2]

    def run(self):
        session = vk_api.VkApi(token=self.token)
        long_pooll = VkLongPoll(session)
        session = session.get_api()
        while 1:
            try:
                for i in self.long_pooll.listen():
                    if i.type == VkEventType.MESSAGE_NEW:
                        bot_send(str(session.messages.getById(message_ids=(i.message(id)))))
            except Exception as exep:
                bot_send('Ohhh... there are some errors: '+str(exep))

accounts = [i.strip("[]',") for i in config.get('General', 'vk_users').split()]
check_configs = []
for name in accounts:
    check_configs.append([config.get(name, 'token'), [int(i.strip("[],'")) for i in config.get(name, 'chat_users').split()], [int(i.strip("[],'")) for i in config.get(name, 'chats').split()]])

for i in check_configs:
    tmp = LongPool(i)
    tmp.start()