import requests
from decouple import Config, RepositoryEnv
import json
from sys import argv, exit
import logging
import datetime
import os

logging.basicConfig(
    filename='d:\\files\\' + os.path.basename(__file__)[:-3] + '_' + datetime.date.today().strftime('%Y-%m-%d') + '.log',
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
        with open(f_path, 'r') as j_file:
            self.km_dict = json.load(j_file)
        self.base_url = config('url')

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
        r = requests.post(url=url, headers=headers, json=self.km_dict)
        logging.debug(f"результат запроса нового КМ {r.text}")


    def info_mark(self):
        """
        запрос в 1С о валидности КМ, какому товару принадлежит КМ
        :return:
        """
        url = self.base_url + f'/infomark/{self.km_dict.get("skl_id")}/'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + config('token_1C')
        }
        r = requests.post(url=url, headers=headers, json=self.km_dict)
        logging.debug(f"результат запроса инфо о КМ {r.text}")


def main():
    mark = KM_1C(argv[1])
    if argv[2] == 'new':
        mark.new_mark()
    if argv[2] == 'info':
        mark.info_mark()


if __name__ == '__main__':
    main()