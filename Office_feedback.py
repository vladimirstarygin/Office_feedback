#!/usr/bin/env python
# coding: utf-8

# In[1]:


from dialog_bot_sdk.bot import DialogBot
from dialog_api import messaging_pb2
from dialog_bot_sdk import interactive_media
import matplotlib.pyplot as plt
import pandas as pd
import grpc
import os
import  utils 
import numpy as np


# In[2]:


def make_statistic_by_all_events(bot,peer):
    
    button_full_stat = interactive_media.InteractiveMediaButton("Full_stat", "Статистика по всем мероприятиям")
    button_download = interactive_media.InteractiveMediaButton("Files", "Выгрузить данные по статистике")    
    bot.messaging.send_message(
        peer,
        " ",
            [interactive_media.InteractiveMediaGroup(
                [
                interactive_media.InteractiveMedia(
                    1,
                    button_full_stat,
                    style = 'default'
                ),
                interactive_media.InteractiveMedia(
                    2,
                    button_download,
                    style = 'default'
                ),
                ]            
            )]
            )


# In[3]:


def make_user_recommendation(bot,peer):
    data = pd.read_csv("Marks.csv")
    data1 = pd.read_csv("Event_type.csv",  encoding ='cp1251',sep=";")
    data["Num_replies"] = 1 
    a = pd.DataFrame(data.groupby(["Id",'Mark',"Event"]).count()).reset_index()
    print(a)
    events = [];
    events_like = list(a[(a["Mark"] == 5)&(a["Id"] == (peer.id))]["Event"].values)
    events_like = events_like + list((a[(a["Mark"] == 4)&(a["Id"] == (peer.id))]["Event"].values))
    events_like = events_like + list(a[(a["Mark"] == '5')&(a["Id"] == (peer.id))]["Event"].values)
    events_like = events_like + list((a[(a["Mark"] == '4')&(a["Id"] == (peer.id))]["Event"].values))
    print(events_like)
    events_type = []
    for i in events_like:
        events_type = events_type + list(data1[data1["Event"] == i]["Type"].values)
    for i in events_type: 
        events = events + list(data1[data1["Type"] == i]["Event"].values)
    events1 = set(events).difference(set(events_like))  
    if (len(events1) == 0):
        bot.messaging.send_message(
        peer, 
        "Ой-ой-ой. Кажется, нам нечего тебе предложить. Оставляй больше оценок по мероприятиям и тогда мы подберем, что-то стоящее." )
    else:
        ev = ", ".join(events1)
        bot.messaging.send_message(
        peer, 
        "👁️‍🗨️Мой искуственный интеллект сделал вывод, что тебе обязательно понравятся мероприятия: "+ str(ev))


# In[4]:


def make_buttons_to_stat(bot,peer,event):
    button_plot = interactive_media.InteractiveMediaButton(event + "plot", "График оценок")
    button_feedbacks = interactive_media.InteractiveMediaButton(event + "feed", "Отзывы")


    bot.messaging.send_message(
        peer,
        "Какую статистику вы хотите?",
            [interactive_media.InteractiveMediaGroup(
                [
                interactive_media.InteractiveMedia(
                    1,
                    button_plot,
                    style = 'primary'
                ),
                interactive_media.InteractiveMedia(
                    2,
                    button_feedbacks,
                    style = 'primary'
                ),
                ]            
            )]
            )


# In[5]:


def make_user_stat(bot,peer):
    data = pd.read_csv("Marks.csv",  encoding ='cp1251')
    fig = plt.figure()
    a = dict(data[data["Id"]==str(peer.id)].groupby('Mark').count()["Event"])
    if(len(a) == 0):
        bot.messaging.send_message(
        peer,
        "Ой-ой, ты не оставил ни одной оценки😔 Если ты не посетил ни одного мероприятия, то смело узнавай информацию и скорее беги на понравившееся.\n Если хочешь написать отзыв о мероприятии, выбирай опцию отзыв, а после этого пиши оценка.",
        ) 
    else:
        patches,text = plt.pie([float(v) for v in a.values()], labels=[str(k) for k in a.keys()], autopct=None) 
        plt.legend(patches, a.keys(), loc="best")
        plt.savefig('img.png')
        bot.messaging.send_image(peer, 'img.png')
        os.remove('img.png')


# In[6]:


def make_admin_stat(bot,peer):
    global admin_stats
    admin_stats = 1
    bot.messaging.send_message(
    peer,
    "Выбери мероприятие, по которому Вы хотите получить статистику. Или же выбери статистику по всем мероприятиям",
    )
    make_event_buttons(bot,peer,"admin")
    make_statistic_by_all_events(bot,peer)


# In[7]:


statistic = 0
passw = 0
admin_users = []
simple_users = []
admin_stats = 0
event_feed = ""


def make_statistics(bot,peer):
    global statistic
    global admin_users 
    global simple_users 
    global admin_stats
    
    if (peer.id in admin_users):
        
        bot.messaging.send_message(
        peer,
        "Да вы же администратор! Выбери мероприятие, по которому Вы хотите получить статистику",
        )
        admin_stats = 1
        make_event_buttons(bot,peer,"admin")
        make_statistic_by_all_events(bot,peer)
    else:   
        if (peer.id in simple_users):
            bot.messaging.send_message(
            peer,
            "Привет мой дорогой пользователь. А вот и твоя круговая диаграмма оценок",
            )
            make_user_stat(bot,params[0].peer)
        else:
            bot.messaging.send_message(
            peer,
            "Окей, время статистики! Но ответь-ка мне на один вопрос:\n Ты случайно не администратор? (Да/нет)",
            )
            statistic = 1
            
    


# In[8]:


def make_mark_buttons(bot,peer):
    global flag_mark
    buttons = []
    for i in range(5):
        buttons.append(interactive_media.InteractiveMedia(str(i+5),interactive_media.InteractiveMediaButton("mark"+str(i+1), str(i+1)),style='danger'))
    bot.messaging.send_message(
        peer,
        "Поставь оценку от 1 - 5",
        [interactive_media.InteractiveMediaGroup(
          buttons
        )]
    )
    flag_mark = 0 
        


# In[9]:


def make_reply_buttons(bot, peer,event):
    global flag_event
    outpeer = bot.manager.get_outpeer(peer) 
    
    button_feedback = interactive_media.InteractiveMediaButton("Feedback1", "Отзыв")
    button_mark = interactive_media.InteractiveMediaButton("Feedback2", "Оценка")
    
    bot.messaging.send_message(
        peer,
        "Очень ждем твоего мнения о " + str(event),
        [interactive_media.InteractiveMediaGroup(
            [
                interactive_media.InteractiveMedia(
                    1,
                    button_feedback,
                    style = 'primary'
                ),
                interactive_media.InteractiveMedia(
                    2,
                    button_mark,
                    style = 'primary'
                ),
            ]            
        )]
    )
    flag_event = 0


# In[10]:


flag_event = 0
flag_reply = 0
flag_mark = 0
flag_reply_from_start = 0
flag_statistics = 0
users = []
def write_descp(bot, peer,descp,event, msg):
    outpeer = bot.manager.get_outpeer(peer)
    global flag_event
    global flag_reply
    bot.messaging.send_message(
        peer, 
        "Краткое описание" + str(event) +'\n' + str(descp)+'\n')
    
    if(msg == 0):
        bot.messaging.send_message(
        peer, 
        "Если ты уже был на этом крутейшем мероприятии и хочешь написать свои впечатления, то оставляй отзыв, и мы обязательно учтём его при подготовке новых классных ивентов🔔\n")
    else:
        flag_reply = 1
        bot.messaging.send_message(
        peer, 
        "Раз ты уже посетил, это мероприятие, пиши всё, что о нём думаешь:).\n")
    flag_event = event

    
    


# In[11]:


def make_event_buttons(bot, peer,msg):
    
    outpeer = bot.manager.get_outpeer(peer)
    history = bot.messaging.load_message_history(outpeer, limit=10, direction=messaging_pb2.LISTLOADMODE_BACKWARD).history

    
    event = pd.read_csv("Events.csv",encoding = 'cp1251', sep =";")
    list_of_events = list(event["Event"].unique())
    buttons = []
    for i in range(len(list_of_events)):
        buttons.append(interactive_media.InteractiveMedia(i,interactive_media.InteractiveMediaButton(list_of_events[i],list_of_events[i]),style = 'primary'))
        
    bot.messaging.send_message(
        peer,
        "Выберите мероприятие",
        [interactive_media.InteractiveMediaGroup(
        buttons
        )]
    )
    
    for msg in history:
        if msg.sender_uid != peer.id:
            return bot.messaging.update_message(msg, msg.message.textMessage.text)


# In[12]:


def on_click(*params):

    global flag_event
    global flag_reply
    global flag_reply_from_start
    global event_feed
    global admin_stats
    uid = params[0].uid
    which_button = params[0].value

    event = pd.read_csv("Events.csv",  encoding ='cp1251', sep=";")
    list_of_events = list(event["Event"].unique())
    events_plot1 = list(event["Event"].unique())
    events_feedbacks1 = list(event["Event"].unique())
    events_plot = []
    events_feedbacks = []
    for i in range(len(events_plot1)):
        events_plot.append(events_plot1[i] + 'plot')
    for i in range(len(events_feedbacks1)):
        events_feedbacks.append(events_feedbacks1[i] + 'feed')

    list_of_marks = []
    for i in range(1, 6):
        list_of_marks.append("mark" + str(i))
    peer = bot.users.get_user_peer_by_id(uid)
    if (which_button == 'Inform'):
        make_event_buttons(bot, peer, "noth")
    if (which_button in list_of_events):
        if (admin_stats):
            make_buttons_to_stat(bot, peer, which_button)
        else:
            write_descp(
                bot, peer,
                event[event["Event"] == which_button]["Description"].values[0],
                which_button, flag_reply_from_start)
    if (which_button == 'Feedback1'):
        flag_reply = 1
        bot.messaging.send_message(
            peer, "Пиши, не стесняйся. Критика - это комплимент😉")
    if (which_button == 'Feedback2'):
        make_mark_buttons(bot, peer)
    if (which_button in list_of_marks):
        bot.messaging.send_message(
            peer,
            "Cпасибо за твою оценку!\nЕсли остались еще предложения или же захочешь посмотреть статистику - пиши мне!"
        )
        data = pd.DataFrame(columns=["Id", 'Event', 'Mark'])
        array = [str(peer.id)] + [str(flag_event)] + [which_button[-1]]
        data.loc[0] = array
        data.to_csv("Marks.csv", mode='a', header=False)
        flag_event = 0
        flag_reply = 0
    if (which_button == 'Feedback'):
        bot.messaging.send_message(peer, "Давай-ка выберем мероприятие.")
        flag_reply_from_start = 1
        make_event_buttons(bot, peer, "")
    if (which_button == 'Stat'):
        make_statistics(bot, peer)
    if (which_button in events_plot):
        data = pd.read_csv("Marks.csv",  encoding ='cp1251')
        fig = plt.figure()
        a = dict(data[data["Event"] == which_button[:-4]].groupby(
            'Mark').count()["Event"])
        if (len(a) == 0):
            bot.messaging.send_message(peer, "К сожалению, по оценкам пока ничего нет")
        else:
            patches, text = plt.pie([float(v) for v in a.values()],
                                    labels=[str(k) for k in a.keys()],
                                    autopct=None)
            plt.title(which_button[:-4])
            plt.legend(patches, a.keys(), loc="best")
            plt.savefig('img.png')
            bot.messaging.send_image(peer, 'img.png')
            os.remove('img.png')
    if (which_button in events_feedbacks):
        data = pd.read_csv("Df_to_pred.csv", error_bad_lines=False,sep =';')
        bot.messaging.send_message(
            peer, "Итак, всего отзывов по этому мероприятию: " +
            str(len(data[data["Event"] == which_button[:-4]]['Target'])))
        event_feed = which_button[:-4]
        bot.messaging.send_message(peer, "Сколько вы хотите посмотреть?")
    if (which_button == 'Reccom'):
        make_user_recommendation(bot, peer)
    if (which_button == 'Full_stat'):
        data = pd.read_csv("Marks.csv")
        data1 = pd.read_csv("Df_to_pred.csv", error_bad_lines=False,sep =';')


        data = data[data["Event"]!='0']
        data1 = data1[data1["Event"]!='0']
        data = data[data["Event"]!=0]
        data1 = data1[data1["Event"]!=0]
        if (len(data) == 0):
            bot.messaging.send_message(peer, "К сожалению, по оценкам пока ничего нет")
        else:
            ax0 = (pd.DataFrame(data.groupby(
                ['Event'])["Id"].count()).rename(columns={
                    "Id": "Количество оценок"
                }).plot(kind='bar', figsize=(25, 10), rot=0))
            ax0.set_title("Количество оценок по мероприятиям", fontsize=36)
            plt.savefig('img.png')
            bot.messaging.send_image(peer, 'img.png')
            os.remove('img.png')
        if (len(data1) == 0):
            bot.messaging.send_message(peer, "К сожалению, по отзывам пока ничего нет")
        else:
            ax1 = (pd.DataFrame(data1.groupby(
                ['Event'])["Id"].count()).rename(columns={
                    "Id": "Количество отзывов"
                }).plot(kind='bar', figsize=(25, 10), rot=0))
            ax1.set_title("Количество отзывов по мероприятиям", fontsize=36)
            plt.savefig('img.png')
            bot.messaging.send_image(peer, 'img.png')
            os.remove('img.png')
    if (which_button == 'Files'):
        bot.messaging.send_file(peer, "Marks.csv")
        bot.messaging.send_file(peer,"Df_to_pred.csv")


# In[13]:


def on_msg(*params):
    global flag_event
    global flag_reply
    global flag_mark
    global statistic
    global passw
    global users
    global admin_users
    global simple_users
    global event_feed
    global statistic
    global admin_stats
    admin_stats = 0
    new = 0
    if params[0].peer.id not in users:
        users.append(params[0].peer.id)
        new = 1

    if (flag_reply == 1):
        bot.messaging.send_message(
            params[0].peer,
            "Спасибо твое мнение учтено! Жди новых новостей о крутых мероприятиях!\nЕсли же ты хочешь еще поставить оценку этому мероприятию, то смело пиши оценка. "
        )
        text = '"' + str(params[0].message.textMessage.text) + '"'
        data = pd.DataFrame(columns=["Id", 'Event', 'Mark'])
        array = [str(params[0].peer.id)] + [str(flag_event)] + [text]
        data.loc[0] = array
        data.to_csv("Df_to_pred.csv", mode="a", header=False)
        flag_reply = 0
        flag_reply_from_start = 0
        flag_mark = 1
    else:
        if ((str(params[0].message.textMessage.text).lower() == 'оценка')
                and (flag_mark != 0)):
            make_mark_buttons(bot, params[0].peer)
        else:
            if ((str(params[0].message.textMessage.text).lower() == 'отзыв')
                    and ((flag_event != 0))):
                make_reply_buttons(bot, params[0].peer, flag_event)

            else:
                if ((str(params[0].message.textMessage.text).lower() == 'да')
                        and (statistic == 1)):
                    params1 = bot.messaging.send_message(
                        params[0].peer,
                        "Сильное заявление. Тогда не введешь ка ли ты пароль?(Так и быть на первый раз пароль admin)"
                    )
                    passw = 1
                else:
                    if ((str(params[0].message.textMessage.text).lower() ==
                         'нет') and ((statistic != 0))):
                        params1 = bot.messaging.send_message(
                            params[0].peer,
                            "Хорошо. Тогда вот тебе диаграмма по твоим отзывам.\nЗдесь ты можешь увидеть статистику своих оценок"
                        )
                        make_user_stat(bot, params[0].peer)
                    else:
                        if ((passw == 1)):
                            if (str(params[0].message.textMessage.text) ==
                                    'admin'):
                                params1 = bot.messaging.send_message(
                                    params[0].peer,
                                    "Вопросов больше не имею. Я тебя запомнил🧐 Теперь у тебя есть доступ к расширенной статистике."
                                )
                                admin_users.append(params[0].peer.id)
                                passw = 0
                                make_admin_stat(bot, params[0].peer)
                            else:
                                if (str(params[0].message.textMessage.text) ==
                                        'stop'):
                                    params1 = bot.messaging.send_message(
                                        params[0].peer,
                                        "Ну что хакер😎, надоело? Только не обижайся:) Интересный факт, если бы в пароле было всего 5 символов, а на каждой позиции стояла бы одна из 32 букв, то тебе бы пришлось перебрать 33554432 вариантов😨\n Не самая трудная задача для компьютера, но кто сказал, что тут 5 символов:)\n О чем это я? Ах да, вот твой допуск к статистике."
                                    )
                                    simple_users.append(params[0].peer.id)
                                    passw = 0
                                    make_user_stat(bot, params[0].peer)
                                else:
                                    params1 = bot.messaging.send_message(
                                        params[0].peer,
                                        "Хм, пароль не подходит😬. Попробуй-ка ещё, либо напиши stop и получи привелегии user-a."
                                    )
                        else:
                            if (event_feed != ''):
                                data = pd.read_csv("Df_to_pred.csv", error_bad_lines=False,sep =';')
                                try:
                                    int(params[0].message.textMessage.text)
                                    if (int(params[0].message.textMessage.text) >
                                        len(data[data["Event"] == event_feed]
                                            ['Target'])):
                                        params1 = bot.messaging.send_message(
                                        params[0].peer,
                                        "Хм, это слишком много, введи ещё раз")
                                    else:
                                        num_feeds = int(
                                        params[0].message.textMessage.text)
                                        params1 = bot.messaging.send_message(
                                        params[0].peer,
                                        "Итак вот отзывы по мероприятию " +
                                        event_feed)

                                        feeds = data[
                                        data["Event"] ==
                                        event_feed]['Target'].values[:]
                                        for i in range(num_feeds):
                                            params1 = bot.messaging.send_message(
                                            params[0].peer, feeds[i])
                                        event_feed = ''
                                except:
                                    params1 = bot.messaging.send_message(
                                        params[0].peer,
                                        "Введи целое число. Не пытайся обмануть меня🤓"
                                        )
                                        
                                            
 
                            else:
                                flag_mark = 0
                                if (new == 1):
                                    params1 = bot.messaging.send_message(
                                        params[0].peer,
                                        "Привет😀 Надеюсь тебе нравятся наши мероприятия🎙️🎵\nЕсли хочешь получить подробную информацию о каждом из них, нажми на кнопку информация.\nЕсли хочешь оставить свой отзыв, жми на соответствующую кнопку."
                                    )
                                else:
                                    params1 = bot.messaging.send_message(
                                        params[0].peer,
                                        "Кажется, мы уже встречались раньше🤔. Хочешь оставить ещё отзывов или узнать больше информации? Одобряю!\nЖми же скорее на кнопку."
                                    )
                                button_inf = interactive_media.InteractiveMediaButton(
                                    "Inform", "Информация")
                                button_feedback = interactive_media.InteractiveMediaButton(
                                    "Feedback", "Отзыв")
                                button_stats = interactive_media.InteractiveMediaButton(
                                    "Stat", "Статистика")
                                button_recommendations = interactive_media.InteractiveMediaButton(
                                    "Reccom", "Рекомендации")
                                bot.messaging.send_message(
                                    params[0].peer, " ", [
                                        interactive_media.
                                        InteractiveMediaGroup([
                                            interactive_media.InteractiveMedia(
                                                1, button_inf,
                                                style='primary'),
                                            interactive_media.InteractiveMedia(
                                                2,
                                                button_feedback,
                                                style='primary'),
                                            interactive_media.InteractiveMedia(
                                                3,
                                                button_stats,
                                                style='primary'),
                                            interactive_media.InteractiveMedia(
                                                4,
                                                button_recommendations,
                                                style='primary'),
                                        ])
                                    ])


# In[14]:


if __name__ == '__main__':
    
    bot = DialogBot.get_secure_bot(
        "hackathon-mob.transmit.im",  # bot endpoint from environment
        grpc.ssl_channel_credentials(), # SSL credentials (empty by default!)
        "be9ca5de6087c9ac19824217526cbd2c61519ada"  # bot token from environment
    )
    

    bot.messaging.on_message(on_msg, on_click)

