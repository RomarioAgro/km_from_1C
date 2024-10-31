import requests
from decouple import Config, RepositoryEnv
import json
from sys import argv, exit
import logging
import datetime
import os
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




def main():
    mark = KM_1C(argv[1])
    if argv[2] == 'new':
        mark.new_mark()
    if argv[2] == 'info':
        exit(mark.info_mark())


if __name__ == '__main__':
    main()