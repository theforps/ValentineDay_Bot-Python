import telebot
import vk_api
import config
from telebot import types
from vk_api import VkUpload
from telebot.types import InputMediaPhoto
import random

print("starting valentine_bot")

bot = telebot.TeleBot(config.API_TG)
token_vk_ref = config.USER_TOKEN_VK
token_vk_atmo = config.GROUP_TOKEN_VK

vk_session_atmo = vk_api.VkApi(token=token_vk_atmo)
vk_atmo = vk_session_atmo.get_api()

vk_session_ref = vk_api.VkApi(token=token_vk_ref)
vk_ref = vk_session_ref.get_api()

users = dict()
future_messages = dict()


@bot.message_handler(content_types=['text', 'photo'])
def get_text_messages(message):
    print(f"{message=}")
    
    try:
        if message.media_group_id != None:
            try:
                
                keyboard = types.InlineKeyboardMarkup()
                key_start = types.InlineKeyboardButton(text='Пойти по верному пути', callback_data='start')
                keyboard.add(key_start)

                bot.send_message(message.from_user.id, "Мне зачем-то пришло больше одной фотографии :3", reply_markup=keyboard)
            except Exception as e:
                print(e)
        elif message.text == "/start":
            bot.send_chat_action(message.from_user.id, action = "typing")
            hello_message(message)

        elif users[message.from_user.id] == 1 and message.content_type == 'photo':
            info = message.from_user.id + message.id
            fileId = message.photo[-1].file_id

            file_info = bot.get_file(fileId)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(f"images/{info}.jpg", 'wb') as new_file:
                new_file.write(downloaded_file)
            
            future_messages[message.from_user.id] = [
                info,
                message.caption
            ]

            vk_user_url(message)

        elif users[message.from_user.id] == 2 and message.text != "":
            future_messages[message.from_user.id] = [
                None, 
                message.text
            ]
            vk_user_url(message)

        elif users[message.from_user.id] == 3 and message.text != "":
            send_vk(message)
        elif users[message.from_user.id] == 1 and message.content_type == 'text':
            error_message(message)
        else:
            try:
                bot.delete_message(chat_id=message.chat.id,message_id=message.id)
            except Exception as e:
                print(e)

    
    except Exception as e:
        print(e)
    

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    print(f"{call=}")

    if call.data == "start":
        try:
            bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=None)
        except Exception as e:
            print(e)
        start_message(call)

    elif call.data == "templ":     
        try:
            bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=None)
        except Exception as e:
            print(e)
        templates(call)

    elif call.data == "text_photo":
        try:
            bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=None)
        except Exception as e:
            print(e)     
        valentine_text_photo(call)

    elif call.data == "text":
        try:
            bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=None)
        except Exception as e:
            print(e)
        valentine_text(call)



def hello_message(message):
    content = "Привет! Я работаю не покладая рук, чтобы отправить валентинку твоему близкому человеку❤\n\n🚨ВАЖНО🚨\n\n- Твой получатель должен быть участником группы \"АТМО-МЫ\"\n\n- У тебя и у твоего получателя должны быть разрешены сообщения от сообщества\n\n- Достаточно один раз нажать на кнопку и дождаться ответа\n\n- Не стоит сильно выходить за рамки этики, потому что не у всех одинаковое чувство юмора (найдем и наругаем)\n\nВсе сообщения полностью анонимные!"
    
    keyboard = types.InlineKeyboardMarkup()
    key_start = types.InlineKeyboardButton(text='Начать', callback_data='templ')
    keyboard.add(key_start)

    img = open('images/start1.jpg', 'rb')

    bot.send_chat_action(message.from_user.id, action = "typing")
    bot.send_photo(message.from_user.id, caption=content, photo=img, reply_markup=keyboard)

    img.close()

def templates(message):

    try:
        media_group = []

        for num in range(1, 11):
            media_group.append(InputMediaPhoto(open(f'images/templates/{num}.jpg', 'rb')))

        keyboard = types.InlineKeyboardMarkup()
        key_start = types.InlineKeyboardButton(text='Далее', callback_data='start')
        keyboard.add(key_start)

        bot.send_chat_action(message.from_user.id, action = "typing")
        bot.send_media_group(message.from_user.id, media=media_group)
        bot.send_chat_action(message.from_user.id, action = "typing")
        bot.send_message(message.from_user.id, text="Ты можешь выбрать одну из наших валентинок)", reply_markup=keyboard)
        
    except Exception as e:
        print(e) 


def start_message(message):

    content = "Ты можешь:\n1) Отправить фотокарточку с текстом или без\n2) Отправить просто текст\n\nВыбери тип валентинки:"

    keyboard = types.InlineKeyboardMarkup()
    key_first = types.InlineKeyboardButton(text='Текст с фото', callback_data='text_photo')
    key_second = types.InlineKeyboardButton(text='Текст без фото', callback_data='text')
    keyboard.add(key_first)
    keyboard.add(key_second)


    users[message.from_user.id] = 0

    try:
        bot.send_chat_action(message.from_user.id, action = "typing")
        bot.send_message(message.from_user.id, text=content, reply_markup=keyboard)
    except Exception as e:
        print(e)



def vk_user_url(message):

    info = future_messages[message.from_user.id]

    if(info[0] == None and info[1] == None):
        error_message(message)
    else:
        keyboard = types.InlineKeyboardMarkup()
        key_start = types.InlineKeyboardButton(text='Назад', callback_data='start')
        keyboard.add(key_start)

        content = "Введи ссылку на ВК твоего получателя в формате https://vk.com или https://vk.me"

        users[message.from_user.id] = 3
        try:
            bot.send_chat_action(message.from_user.id, action = "typing")
            bot.send_message(message.from_user.id, text=content, disable_web_page_preview=True, reply_markup=keyboard)
        except Exception as e:
            print(e)



def send_vk(message):

    try:
        user_url = message.text
        userId = 0
        userDomain = ""
        attachment = ""

        if ("https://vk.com/id" in user_url and isinstance(user_url.replace("https://vk.com/id", ""), int)):
            userId = int(user_url.replace("https://vk.com/id", ""))
        elif "https://vk.com/" in user_url:
            userDomain = user_url.replace("https://vk.com/", "")
        elif "https://vk.me/" in user_url:
            userDomain = user_url.replace("https://vk.me/", "")

        info = future_messages[message.from_user.id]
        user_message = ""

        if(info[1] != None):
            user_message = info[1]

        if(info[0] != None):
            upload = VkUpload(vk_ref)
            photo = upload.photo(
                photos=f'images/{str(info[0])}.jpg', 
                group_id=f"{config.GROUP_ID}", 
                album_id=f"{config.ALBUM_ID}"
            )
            owner_id = photo[0]['owner_id']
            photo_id = photo[0]['id']
            attachment = f'photo{owner_id}_{photo_id}'
        
        vk_atmo.messages.send(
            user_id = userId,
            random_id=random.randint(1, 9999999), 
            attachment=attachment, 
            domain=userDomain, 
            message=f"💌Вам пришла валентинка:\n\n {user_message} \n\nВы можете отправить свою валентинку по ссылке: t.me/atmo_valentine_bot"
        )

        if(info[0] != None):
            import os
            os.remove(f'images/{str(info[0])}.jpg')

        print(message.from_user.username + " " + message.text)

        json_data = f"sender : {message.from_user.username},\nrecipient : {message.text},\ntext : {info[1]}\n\n"

        
        file_object = open('log.txt', 'a', -1, 'UTF-8')
        file_object.write(json_data)
        file_object.close()


        users[message.from_user.id] = 0
        future_messages[message.from_user.id] = []

        keyboard = types.InlineKeyboardMarkup()
        key_start = types.InlineKeyboardButton(text='Отправить снова', callback_data='start')
        keyboard.add(key_start)

        bot.send_chat_action(message.from_user.id, action = "typing")
        bot.send_message(message.from_user.id, "Валентинка успешно отправлена!", reply_markup=keyboard)
    except Exception as e:

        info = future_messages[message.from_user.id]
        if(info[0] != None):
            import os
            os.remove(f'images/{str(info[0])}.jpg')

        print(e)
        error_message(message)



def error_message(message):

    keyboard = types.InlineKeyboardMarkup()
    key_start = types.InlineKeyboardButton(text='Назад', callback_data='start')
    keyboard.add(key_start)

    try:
        bot.send_chat_action(message.from_user.id, action = "typing")
        bot.send_message(message.from_user.id, "Не выполнены все требования или твой получатель не разрешил себе отправлять сообщения😞\n\nПопробуй еще раз\n", reply_markup=keyboard)
    except Exception as e:
        print(e)


def valentine_text_photo(message):

    users[message.from_user.id] = 1

    keyboard = types.InlineKeyboardMarkup()
    key_back = types.InlineKeyboardButton(text='Назад', callback_data='start')
    keyboard.add(key_back)

    try:
        bot.send_chat_action(message.from_user.id, action = "typing")
        bot.send_message(message.from_user.id, "\nОтправь фото и текст (по желанию) в одном сообщении\n", reply_markup=keyboard)
    except Exception as e:
        print(e)



def valentine_text(message):

    users[message.from_user.id] = 2

    keyboard = types.InlineKeyboardMarkup()
    key_back = types.InlineKeyboardButton(text='Назад', callback_data='start')
    keyboard.add(key_back)
    try:
        bot.send_chat_action(message.from_user.id, action = "typing")
        bot.send_message(message.from_user.id, "\nОтправь текст в одном сообщении\n", reply_markup=keyboard)
    except Exception as e:
        print(e)
        

bot.polling(none_stop=True, interval=0)