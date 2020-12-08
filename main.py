from captcha_solver import CaptchaSolver
from saver import Saver
import requests as req
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import io
from collections import namedtuple
from russian_names import RussianNames
from TEMP_mail.tempmail import *
import random
import logging
from PIL import Image
import re
import time
import datetime
from os import getenv

# Получаем все privacy данные из переменных окружения
rucaptcha_API_key = getenv("rucaptcha_API_key")

solver = CaptchaSolver('rucaptcha', api_key=rucaptcha_API_key)
saver = Saver("data.csv")

domain = "https://org.mephi.ru/"
N = 40  # Количество аккаунтов, которые необходимо зарегать.
Person = namedtuple("Person", ["name", "surname", "f_name", "password", "email"])


def generate_random_date(year):
    """Generate random string object. Date in the year in this format dd.mm.yyyy."""
    # time_between_dates = end_date - start_date
    # days_between_dates = time_between_dates.days
    # random_number_of_days = random.randrange(days_between_dates)
    # random_date = start_date + datetime.timedelta(days=random_number_of_days)
    # if __name__ == '__main__':
    #     result = random_date.days + "." + random_date.
    # return random_date
    # TODO Do it using datetime
    day = random.randint(1, 25)
    month = random.randint(1, 12)
    return str(day) + "." + str(month) + "." + str(year)


def generate_passport_data():
    return str(random.randint(1000, 9999)), str(random.randint(100000, 999999),), "ОУФМС РОССИИ ПО ГОР. МСК в окр. БИРЮЛЁВО" + str(random.randint(1, 5))


def generate_phone():
    return "+7928" + str(random.randint(1011110, 9999999))


def generate_city():
    return "Москва"


def find_link(string: str):
    """Find first link (url) in string sing regex. Works too bad. So we need a lot of splits and replaces to make it work
    at least somehow """
    return str(re.search("(?P<url>https?://[^\s]+)", string).group("url"))


def generate_password(length=7):
    letters = 'abcdefghijklmnopqrstuvwxyz123456789ABCDEFGHIGKLMNOPQRSTUVWXYZ'
    return ''.join([random.choice(letters) for n in range(length)])


def save_image_by_link(link: str, file_name="res.png"):
    """save file with filename.png to scripts dir"""
    r = req.get(link, stream=True)
    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            for chunk in r:
                f.write(chunk)


def get_image_by_link(link: str):
    """Returns bytes - image"""
    response = req.get(link)
    image_bytes = io.BytesIO(response.content)
    return image_bytes


def save_requests_to_file(text, file_name="res.html"):
    with open(file_name, "wb") as f:
        f.write(text)


for i in range(N):
    session = req.session()
    r = session.get("https://org.mephi.ru/register/pupil")
    soup = bs(r.content, "html.parser")
    captcha_image_link_rel = soup.find_all("img")[-1].get("src")
    captcha_id = captcha_image_link_rel.split("/")[-1].replace(".png", "")
    captcha_image = get_image_by_link(urljoin(domain, captcha_image_link_rel))
    captcha_text = solver.solve_captcha(captcha_image.getvalue())

    # Выбираем случайный слушатель почты
    mail_listener_num = random.randint(1, 4)
    if mail_listener_num == 1:
        mail_listener = Guerilla()
    elif mail_listener_num == 2:
        mail_listener = Fakemail()
    elif mail_listener_num == 3:
        mail_listener = NADA()
    else:
        mail_listener = TempTop()
    name, surname, f_name = RussianNames().get_person().split()
    date_of_birth = generate_random_date(2003)

    login = mail_listener.email
    password = generate_password()

    # Делаем запрос на сайт Росатом для регистрации нового аккаунта
    request = (
        session.post("https://org.mephi.ru/register/pupil",
                     data={"register_type": "olympRos", "id": "", "code": "", "email": login, "password": password,
                           "password_confirm": password, "lastname": surname, "firstname": name, "secondname": f_name,
                           "date_of_birth": "16.12.2004", "cel_phone": "", "vuz": 0, "otherVUZ": "", "course": "",
                           "VUZCountry": 3159, "citizenship": 3159, "vuzRegionId": "", "vuzRegion": "", "vuzCityId": "",
                           "vuzCity": "", "agree": 1, "captcha[id]": captcha_id,
                           "captcha[input]": captcha_text}).content)  # TODO Add date birth generator

    print(login, password, "REGISTERED")
    saver.add_person(login, password, name, surname, f_name, date_of_birth)

    time.sleep(25)
    # Ожидаем новую почту
    new_mails = []
    while True:
        new_mails = mail_listener.getMessages()[0]
        print(new_mails)
        try:
            if new_mails[-1][1] == "noreply@mephi.ru":
                break
        except IndexError:
            pass
        time.sleep(20)
    reg_mail = mail_listener.getMessage(email_id=new_mails[-1][0])

    link_to_activate = find_link(reg_mail).replace("</a>", "").split('"')[0]
    print(link_to_activate)
    save_requests_to_file(session.get(link_to_activate).content)
    print("USER CONFIRMED EMAIL")
    # Пользователь входит
    session.post("https://org.mephi.ru/auth/login", data={"uname": login, "password": password})

    # Теперь он должен ввести данные
