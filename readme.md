Инструмент для автоматической перемаркировк
 Магазин через сбис заказывает коды маркировки (это первая функция), 1C обрабатывает эти коды с какой то периодичностью и высылаем в магазин им этикетку в битриксе. Они ее печатают, наклеивают на товар и пытаются просканировать в чек в сбисе. в сбис этого кода нет, в этот момент он посылает код во вторую функцию и 1с в ответе выдает штрихкод (13 символьный). Ты по этому штрихкоду создаем код маркировки в сбисе. После чего сможем продать этот код.
info_mark
в теле запроса должен быть параметр code с кодом маркировки, в ответе получишь
либо ошибку (код ответа = 400), если кода нет в нашей базе
либо в теле ответа штрихкод (код ответа = 200)