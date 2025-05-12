import asyncio     #загружаем библеоеки
import python_weather
import telebot 
import schedule
import time
import threading
#from datetime import datetime
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from functools import partsttial
bot = telebot.TeleBot('asdasd')  #бот

what_country = False  #проверка что страна выбрана
country = None  #страна в которой мы проверяем погоду

@bot.message_handler(commands=["start"])  #начальное сообщение
def start(message):
    bot.send_message(message.chat.id, "Здравствуйте! это бот который будет присылать прогнох погоды каждый день прогноз погоды. Чтобы начать напишите /wheather")


@bot.message_handler(commands=["wheather"])  #задаём вопрос о месте погоды
def whatcountry(message):
    bot.send_message(message.chat.id, "Напишите какой страны или города вам нужен прогноз погоды например: Париж, Россия")


@bot.message_handler()
def callback_inline(message):  #выбор страны и запуск напоминания
    global what_country
    global country
    if what_country == False:
        country = message.any_text
        text = asyncio.run(get_weather(country))
        what_country = True
        bot.reply_to(message, text)
        shedule(message)  
       

def shedule(message):  #вопрос о напоминании погоды каждый день
    keyboard = InlineKeyboardMarkup()  #создание кнопок
    btn1 = InlineKeyboardButton(text="да", callback_data="yes")
    btn2 = InlineKeyboardButton(text="нет", callback_data="no")
    keyboard.add(btn1, btn2)
    bot.send_message(message.chat.id, "хотелибы вы поставить прогноз погоды каждый день на 8:00 по заданой стране?", reply_markup=keyboard)

def sync_weather_wrapper(id, country):  #Обертка для запуска асинхронной функции в синхронном коде
    text = asyncio.run(get_weather(country))
    bot.send_message(id, text)

async def get_weather(text):  #присылание сообщения о погоде
    async with python_weather.Client(unit=python_weather.METRIC) as client:
        weather = await client.get(text)
        text = f"""
        Погода в {weather.country}:
        - Температура: {weather.temperature}°C
        - Ощущается как: {weather.feels_like}°C
        - Влажность: {weather.humidity}%
        - Ветер: {weather.wind_speed} км/ч
        - Описание: {weather.description}
        """
        return text

@bot.callback_query_handler(func=lambda call: call.data == "yes" or call.data == "no")  #обработчик ответа об напоминаниях
def callback(call):
    global country
    if call.data == "yes":
        time = "08:00"
        bot.send_message(call.message.chat.id, "Теперь вам каждый день в "+time+" будет присылаться прогноз погоды")
        schedule.every().day.at(time).do(sync_weather_wrapper ,call.message.chat.id, country)
    elif call.data == "no":
        bot.send_message(call.message.chat.id, "Хорошо досвидания")

def run_schedule():  #запуск напоминания
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=run_schedule).start()

bot.polling(non_stop=True) #запуск программы

