import os
import telebot
from dotenv import load_dotenv
from pprint import pprint
from chat import GPT
import workYDB
import json
#from workBitrix import *
from helper import *
from workRedis import *
from createKeyboard import *

load_dotenv()

gpt = GPT()
GPT.set_key(os.getenv('KEY_AI'))
bot = telebot.TeleBot(os.getenv('TELEBOT_TOKEN'))
# инициализация бота и диспетчера
#dp = Dispatcher(bot)
sql = workYDB.Ydb()
#expert_promt = gpt.load_prompt('https://docs.google.com/document/d/181Q-jJpSpV0PGnGnx45zQTHlHSQxXvkpuqlKmVlHDvU/edit?usp=sharing')
#answer = gpt.answer(expert_promt, 
#           'Я хочу, чтобы после завершения обучения мне подобрали работу')
#print(answer)
#testModel = 'https://docs.google.com/document/d/1PIdVe-fmX8DtAIJOx2g65b8SGrVs30C7OGeeMFLNppk/edit?usp=sharing'





@bot.message_handler(commands=['addmodel'])
def add_new_model(message):
    sql.set_payload(message.chat.id, 'addmodel')
    bot.send_message(message.chat.id, 
        "Пришлите ссылку model google document и через пробел название модели (model1). Не используйте уже существующие названия модели\n Внимани! конец ссылки должен вылядить так /edit?usp=sharing",)

@bot.message_handler(commands=['addpromt'])
def add_new_model(message):
    sql.set_payload(message.chat.id, 'addpromt')
    bot.send_message(message.chat.id, 
        "Пришлите ссылку promt google document и через пробел название промта (promt1). Не используйте уже существующие названия модели\n Внимани! конец ссылки должен вылядить так /edit?usp=sharing",)
    

@bot.message_handler(commands=['help', 'start'])
def say_welcome(message):
    #row = {'id': 'Uint64', 'MODEL_DIALOG': 'String', 'TEXT': 'String'}
    #sql.create_table(str(message.chat.id), row)
    #row = {'id': message.chat.id, 'payload': '',}
    #sql.replace_query('user', row)
    bot.send_message(message.chat.id,'/addmodel добавление новой модели\n/model1 - модель 1 Просто обычный чат /context сбросит контекст по текущей модели\nДоюавление моделей кроме model1 пока нельзя\n/restart перезапись главного документа', 
                     parse_mode='markdown')
#expert_promt = gpt.load_prompt('https://docs.google.com/document/d/181Q-jJpSpV0PGnGnx45zQTHlHSQxXvkpuqlKmVlHDvU/')
@bot.message_handler(commands=['context'])
def send_button(message):
    #payload = sql.get_payload(message.chat.id)
    

    #answer = gpt.answer(validation_promt, context, temp = 0.1)
    #sql.delete_query(message.chat.id, f'MODEL_DIALOG = "{payload}"')
    sql.set_payload(message.chat.id, ' ')
    row = {'id': message.chat.id, 'model':'', 'promt':''}
    sql.replace_query('user', row)
    #bot.send_message(message.chat.id, answer)
    clear_history(message.chat.id)
    bot.send_message(message.chat.id, 
        "Контекст сброшен",)

@bot.message_handler(commands=['model'])
def select_model(message):
    #payload = sql.get_payload(message.chat.id)
    models= sql.get_models()
    #print(models)
    keyboard = create_keyboard_is_row(models)
    sql.set_payload(message.chat.id, 'model')
    bot.send_message(message.chat.id,'Выберите модель',reply_markup=keyboard)

@bot.message_handler(commands=['promt'])
def select_promt(message):
    #payload = sql.get_payload(message.chat.id)
    promts = sql.get_promts()
    #print(promts)
    keyboard = create_keyboard_is_row(promts)
    sql.set_payload(message.chat.id, 'promt')
    bot.send_message(message.chat.id,'Выберите промт',reply_markup=keyboard)

@bot.message_handler(content_types=['text'])
def any_message(message):
    #print('это сообщение', message)
    #text = message.text.lower()
    text = message.text
    userID= message.chat.id
    payload = sql.get_payload(userID)
    print(f'{payload=}')
    modelUrl = None
    promtUrl = None
    promt = None
    model_index = None

    modelIndexUser = sql.get_model_for_user(userID)
    promtUser = sql.get_promt_for_user(userID)
    modelIndexUrl = sql.get_model_url(modelIndexUser)
    promtUrl = sql.get_promt_url(promtUser)

    if payload == 'addmodel':
        text = text.split(' ')
        rows = {'model': text[1], 'url': text[0] }
        sql.replace_query('model',rows)
        return 0
    
    if payload == 'addpromt':
        text = text.split(' ')
        rows = {'promt': text[1], 'url': text[0] }
        sql.replace_query('prompt',rows)
        return 0
    
    if payload == 'promt':
        #promtUrl = sql.get_promt_url(text)
        sql.set_payload(message.chat.id, '')
        row = {'promt':text}
        sql.update_query('user', row, f'id={userID}')
        #sql.replace_query('user', row)
        return 0

    if payload == 'model':     
        modelUrl = sql.get_model_url(text)
        sql.set_payload(message.chat.id, '')
        row = {'model':text}
        sql.update_query('user', row, f'id={userID}')
        #model_index=gpt.load_search_indexes(modelUrl)
        #sql.set_payload(message.chat.id, '')
        return 0
        
   
    add_message_to_history(userID, 'user', text)
    history = get_history(str(userID))
    
    #print(f'{promtUrl=}')
    #print(f'{modelIndexUrl=}')
    #print(f'{history}')
    try:
        if promtUrl is not None and modelIndexUrl is not None:
            promt = gpt.load_prompt(promtUrl)
            modelIndex = gpt.load_search_indexes(modelIndexUrl)
            answer = gpt.answer_index(promt, text, history, modelIndex)
        elif promtUrl is not None:
            promt = gpt.load_prompt(promtUrl)
            answer = gpt.answer(promt, history=history)
        elif modelIndexUrl is not None:
            modelIndex = gpt.load_prompt(modelIndexUrl)
            #modelIndex = gpt.load_search_indexes(modelIndexUrl)
            answer = gpt.answer(modelIndex, history=history)
        #bot.send_message(userID, answer)
        #return 0
    except Exception as e:
        history = get_history(str(userID))
        history.pop(1)
        history.pop(1)
        history.pop(1)
        history.pop(1)
        add_old_history(userID,history)
        print(f'{history}=') 
        if promtUrl is not None and modelIndexUrl is not None:
            promt = gpt.load_prompt(promtUrl)
            modelIndex = gpt.load_search_indexes(modelIndexUrl)
            answer = gpt.answer_index(promt, text, history, modelIndex)
        elif promtUrl is not None:
            promt = gpt.load_prompt(promtUrl)
            answer = gpt.answer(promt, history=history)
        elif modelIndexUrl is not None:
            modelIndex = gpt.load_prompt(modelIndexUrl)
            #modelIndex = gpt.load_search_indexes(modelIndexUrl)
            answer = gpt.answer(modelIndex, history=history)
        bot.send_message(userID, e)
        
        #return 0
    #bot.send_message(userID, answer)
    #try:
    add_message_to_history(userID, 'assistant', answer)
    bot.send_message(message.chat.id, answer)
    
    #except Exception as e:
    #    bot.send_message('?')

bot.infinity_polling()
    #answer = gpt.answer(model, history)
    #answer = gpt.answer_index(model, text, model_index,)
    #answer = gpt.answer_index(model, text, history, model_index, verbose=1)
    #answer, answerBlock = gpt.answer_index(model, context, model_index, verbose=1)


    # commands = ['addNew']
    # comandInText = find_word(text,commands)
    # if comandInText == 'addNew':
    #     name = slice_str(answer, 'Имя:','$')
    #     phone = slice_str(answer, 'Номер телефона:','#')
    #     color = slice_str(answer, 'Цвет:','$:')
    #     row = {'TITLE': f'{userID}',
    #            'DESCTIPRION': f'{name} \n{phone} \n{color}'}
    #     dealID = create_deal(row) 
    #     print('создана сделка {dealID}')
    # print('answer', answer)
    #for i in answerBlock:
    #    bot.send_message(message.chat.id, i)
    
    #if payload == 'model3':
    #rows = {'id': time_epoch(),'MODEL_DIALOG': payload, 'TEXT': f'клиент: {text}'}
    #sql.insert_query(userID,  rows)

    #rows = {'id': time_epoch()+1,'MODEL_DIALOG': payload, 'TEXT': f'менеджер: {answer}'}
    #sql.insert_query(userID,  rows)

