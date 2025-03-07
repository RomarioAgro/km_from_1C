import requests
from decouple import Config, RepositoryEnv
import json
from sys import argv, exit
import logging
import datetime
import os
import re
import ctypes
PATH_LOG = 'd:\\files\\'


logging.basicConfig(
    filename=PATH_LOG + os.path.basename(__file__)[:-3] + '_' + datetime.date.today().strftime('%Y-%m-%d') + '.log',
    filemode='a',
    level=logging.DEBUG,
    format="%(asctime)s - %(filename)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S')

# Создание объекта конфигурации
config = Config(RepositoryEnv(os.path.dirname(os.path.abspath(__file__)) + '\\mark.env'))


class KM_1C:
    def __init__(self, f_path):
        """
        класс заказа КМ из базы 1С, либо перемаркировка
        проверка КМ в базе 1С
        :param f_path:
        """
        self.token = config('token_1C')
        try:
            with open(f_path, 'r') as j_file:
                self.km_dict = json.load(j_file)
        except Exception as exs:
            logging.debug(f'ошибка чтения словаря КМ {exs}')
            self.km_dict = {}
        self.base_url = config('url')

    def type_mark(self, tid: str = '222'):
        """
        запрос в 1с за типом маркировки товара
        tid tID товара, какой-то айдишник в системе 1С, обычно это ШК
        :return:
        """
        url = self.base_url + '/infotovar/' + tid
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + self.token
        }
        try:
            r = requests.get(url=url, headers=headers)
        except Exception as exc:
            logging.debug(f"ошибка запроса о типе маркировке {exc}")
            ctypes.windll.user32.MessageBoxW(0, r.json()['message'], 'ошибка', 4096 + 16)
        logging.debug(f"результат запроса о типе маркировке {r.text}")
        if r.json().get('name', '') == '':
            ctypes.windll.user32.MessageBoxW(0, 'ошибка получения типа маркировки', 'ошибка', 4096 + 16)
            return 1111
        mtype = r.json().get('marktype', 5408)
        return mtype

    def new_mark(self):
        """
        запрос в 1с за новой маркой
        :return:
        """
        url = self.base_url + '/newmark/' + self.km_dict.get("skl_id", None)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + self.token
        }
        try:
            r = requests.post(url=url, headers=headers, json=self.km_dict)
        except Exception as exc:
            logging.debug(f"ошибка запроса нового о КМ {exc}")
        logging.debug(f"результат запроса нового КМ {r.text}")


    def info_mark(self):
        """
        запрос в 1С о валидности КМ, какому товару принадлежит КМ
        :return:
        """
        url = self.base_url + f'/infomark/{self.km_dict.get("skl_id")}'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + config('token_1C')
        }
        km = self.km_dict.get('sost')[0].get("code")
        param = {
            "code": km
        }
        logging.debug(f"json = {param}")
        decoded_text = 'пока ошибок нет'
        try:
            r = requests.post(url=url, headers=headers, json=param)
            decoded_text = r.content.decode('utf-8')
        except Exception as exc:
            logging.debug(f"ошибка запроса инфо о КМ {exc} {decoded_text}")
            return 401
        print(decoded_text)
        file_name = os.path.splitext(os.path.basename(argv[1]))[0]
        logging.debug(f"результат запроса инфо о КМ {decoded_text}")
        if r.status_code == 200:
            with open(PATH_LOG + file_name + '_answer.txt', 'w') as f_km:
                f_km.write(r.text)
        return r.status_code

    def freemarkcontent(self):
        """
        есть некий пул КМ которые не распечатаны
        запрос за списком страниц этого пула, их статус в сбис, загружены или нет
        :return: int
        """
        url = self.base_url + f'/freemarkcontent/{self.km_dict.get("skl_id")}'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + config('token_1C')
        }
        decoded_text = 'пока ошибок нет'
        try:
            r = requests.get(url=url, headers=headers)
            decoded_text = r.content.decode('utf-8')
        except Exception as exc:
            logging.debug(f"ошибка запроса об пул км {exc} {decoded_text}")
            return 401
        print(decoded_text)
        file_name = os.path.splitext(os.path.basename(argv[1]))[0]
        logging.debug(f"результат запроса инфо пул км {decoded_text}")
        if r.status_code == 200:
            ids_with_false_status = list(map(lambda item: item['id'], filter(lambda item: item['uploaded'] is False, r.json())))
            with open(PATH_LOG + file_name + '.txt', 'w') as f_lp:
                f_lp.write(','.join(ids_with_false_status))
        return r.status_code

    def freemarkcontent_getpage(self, page: str = '1'):
        """
        получение содержимого пула свободных КМ по номеру страницы
        :return:
        """
        url = self.base_url + f'/freemark/{self.km_dict.get("skl_id")}/{page}'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + config('token_1C')
        }
        decoded_text = 'пока ошибок нет'
        try:
            r = requests.get(url=url, headers=headers)
            decoded_text = r.content.decode('utf-8')
        except Exception as exc:
            logging.debug(f"ошибка запроса состава страницы пула км  {exc} {decoded_text}")
            return 401
        file_name = os.path.splitext(os.path.basename(argv[1]))[0]
        logging.debug(f"результат запроса состава страницы пула км {decoded_text}")
        if r.status_code == 200:
            new_data = [(item['barcod'], item['markFull']) for item in r.json()]
            with open(PATH_LOG + file_name + '_page_' + page + '.txt', 'w') as f_km:
                for elem in new_data:
                    mrk = re.sub(r"[\x1D]", "", elem[1])  # \x1D - шестнадцатеричное представление ASCII 29
                    f_km.write(f'{elem[0]}delimeter{mrk}\n')
        return r.status_code

    def freemarkcontent_closepage(self, page: str = '1'):
        """
        закрытие страницы с КМ из пула свободных
        :return:
        """
        url = self.base_url + f'/freemark/{self.km_dict.get("skl_id")}/{page}'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + config('token_1C')
        }
        decoded_text = 'пока ошибок нет'
        try:
            r = requests.put(url=url, headers=headers)
            decoded_text = r.content.decode('utf-8')
        except Exception as exc:
            logging.debug(f"ошибка запроса закрытия страницы пула км  {exc} {decoded_text}")
            return 401
        logging.debug(f"результат запроса закрытия страницы пула км {decoded_text}")
        print(r.text)
        return r.status_code



def main():
    mark = KM_1C(argv[1])
    if argv[2] == 'new':
        mark.new_mark()
    if argv[2] == 'info':
        exit(mark.info_mark())
    if argv[2] == 'freepoollistpage':
        mark.freemarkcontent()
    if argv[2] == 'freepoolgetpage':
        mark.freemarkcontent_getpage(page=mark.km_dict.get('page', None))
    if argv[2] == 'freepoolclosepage':
        mark.freemarkcontent_closepage(page=mark.km_dict.get('page', None))
    if argv[1] == 'typemark':
        marktype = mark.type_mark(tid=argv[2])
        exit(marktype)


if __name__ == '__main__':
    main()