import telebot
import vk_api
import config
from telebot import types
from vk_api import VkUpload



bot = telebot.TeleBot(config.API_TG)
token_vk_ref = config.USER_TOKEN_VK
token_vk_atmo = config.GROUP_TOKEN_VK

vk_session_atmo = vk_api.VkApi(token=token_vk_atmo)
vk_atmo = vk_session_atmo.get_api()

vk_session_ref = vk_api.VkApi(token=token_vk_ref)
vk_ref = vk_session_ref.get_api()

count_cards = dict()
users = dict()
future_messages = dict()



@bot.message_handler(content_types=['text', 'photo'])
def get_text_messages(message):
    if count_cards.get(message.from_user.id) == None:
        count_cards[message.from_user.id] = 10

    if count_cards[message.from_user.id] == 0:
        bot.send_message(message.from_user.id, text="К сожалению, у тебя закончились валентинки😨\n\nНадеюсь, ты отправил всем, кому хотел🍓\n")

    elif message.text == "/start":

        hello_message(message)

    elif users[message.from_user.id] == 1 and message.caption != "" and message.photo != "":
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

    elif users[message.from_user.id] == 3 and message.photo != "":
        info = message.from_user.id + message.id
        fileId = message.photo[-1].file_id

        file_info = bot.get_file(fileId)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(f"images/{info}.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)
        
        future_messages[message.from_user.id] = [
            info,
            None
        ]
        vk_user_url(message)

    elif users[message.from_user.id] == 4 and message.text != "":
        send_vk(message)

    try:
        bot.delete_message(chat_id=message.chat.id,message_id=message.id)
    except:
        print
    try:
        bot.delete_message(chat_id=message.chat.id,message_id=message.id-1)
    except:
        print



@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if count_cards[call.from_user.id] == 0:
        valentint_limit(call)
    elif call.data == "text_photo":
        valentine_text_photo(call)
    elif call.data == "text":
        valentine_text(call)
    elif call.data == "photo":
        valentine_photo(call)
    elif call.data == "start":
        start_message(call)
    bot.delete_message(chat_id=call.from_user.id,message_id=call.message.message_id)









def hello_message(message):
    content = "Привет! Этот бот работает не покладая рук, чтобы отправить валентинку твоему близкому человеку❤\n\n🚨ВАЖНО🚨\n\n- Твой получатель должен быть участником группы \"Атмо - мы\"\n\n- У тебя и у твоего получателя должны быть разрешены сообщения от сообщества\n"
    
    keyboard = types.InlineKeyboardMarkup()
    key_start = types.InlineKeyboardButton(text='Начать', callback_data='start')
    keyboard.add(key_start)

    img = open('images/start1.jpg', 'rb')

    bot.send_photo(message.from_user.id, caption=content, photo=img, reply_markup=keyboard)

    img.close()



def start_message(message):

    content = "У тебя осталось " + str(count_cards[message.from_user.id]) + " валентинок.\n\nВыбери тип валентинки:"

    keyboard = types.InlineKeyboardMarkup()
    key_first = types.InlineKeyboardButton(text='Текст с фото', callback_data='text_photo')
    key_second = types.InlineKeyboardButton(text='Текст без фото', callback_data='text')
    key_thirst = types.InlineKeyboardButton(text='Фото без текста', callback_data='photo')
    keyboard.add(key_first)
    keyboard.add(key_second)
    keyboard.add(key_thirst)

    users[message.from_user.id] = 0

    bot.send_message(message.from_user.id, text=content, reply_markup=keyboard)



def vk_user_url(message):

    info = future_messages[message.from_user.id]

    if(info[0] == None and info[1] == None):
        error_message(message)
    else:
        content = "Введите ссылку на ВК вашего получателя в формате https://vk.com\n\n😸"

        users[message.from_user.id] = 4

        bot.send_message(message.from_user.id, text=content)



def send_vk(message):

    try:
        user_url = message.text
        userId = 0
        userDomain = ""
        attachment = ""

        if ("https://vk.com/id" in user_url and isinstance(user_url.replace("https://vk.com/id", ""), int)):
            userId = int(user_url.replace("https://vk.com/id", ""))
        else:
            userDomain = user_url.replace("https://vk.com/", "")

        info = future_messages[message.from_user.id]

        if(info[0] != None):
            upload = VkUpload(vk_ref)
            photo = upload.photo(
                photos=f'images/{str(info[0])}.jpg', 
                group_id="224618778", 
                album_id="301477123"
            )
            owner_id = photo[0]['owner_id']
            photo_id = photo[0]['id']
            attachment = f'photo{owner_id}_{photo_id}'
        
        vk_atmo.messages.send(
            user_id = userId,
            random_id=0, 
            domain=userDomain, 
            message="Вам пришла валентинка: "
        )

        vk_atmo.messages.send(
            user_id = userId,
            random_id=0, 
            attachment=attachment, 
            domain=userDomain, 
            message=info[1]
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
        count_cards[message.from_user.id] = count_cards[message.from_user.id] - 1

        keyboard = types.InlineKeyboardMarkup()
        key_start = types.InlineKeyboardButton(text='Назад', callback_data='start')
        keyboard.add(key_start)

        bot.send_message(message.from_user.id, "Валентинка успешно отправлена!", reply_markup=keyboard)
    
    except:
        error_message(message)



def error_message(message):

    keyboard = types.InlineKeyboardMarkup()
    key_start = types.InlineKeyboardButton(text='Назад', callback_data='start')
    keyboard.add(key_start)

    bot.send_message(message.from_user.id, "Что-то было введено неверно или твой получатель не разрешил себе отправлять сообщения😞\n\nПопробуйте снова.\n", reply_markup=keyboard)



def valentine_text_photo(message):

    users[message.from_user.id] = 1

    keyboard = types.InlineKeyboardMarkup()
    key_back = types.InlineKeyboardButton(text='Назад', callback_data='start')
    keyboard.add(key_back)

    bot.send_message(message.from_user.id, "\nОтправьте фото и текст в одном сообщении.\n", reply_markup=keyboard)



def valentine_text(message):

    users[message.from_user.id] = 2

    keyboard = types.InlineKeyboardMarkup()
    key_back = types.InlineKeyboardButton(text='Назад', callback_data='start')
    keyboard.add(key_back)

    bot.send_message(message.from_user.id, "\nОтправьте текст в одном сообщении.\n", reply_markup=keyboard)



def valentine_photo(message):

    users[message.from_user.id] = 3

    keyboard = types.InlineKeyboardMarkup()
    key_back = types.InlineKeyboardButton(text='Назад', callback_data='start')
    keyboard.add(key_back)

    bot.send_message(message.from_user.id, "\nОтправьте фото в одном сообщении.\n", reply_markup=keyboard)



def valentint_limit(message):
    
    bot.send_message(message.from_user.id, text="К сожалению, у тебя закончились валентинки😨\n\nНадеюсь, ты отправил всем, кому хотел🍓\n")



bot.polling(none_stop=True, interval=0)