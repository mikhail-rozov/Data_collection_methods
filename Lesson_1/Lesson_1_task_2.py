"""
2. Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.
"""

import requests
import json

url = "https://calorieninjas.p.rapidapi.com/v1/nutrition"

querystring = {"query": "lemon"}

with open('key.txt', 'r') as key_file:
    key = key_file.readline()

headers = {
    'x-rapidapi-host': "calorieninjas.p.rapidapi.com",
    'x-rapidapi-key': f"{key}"
    }

response = requests.get(url, headers=headers, params=querystring)
data = json.loads(response.text)

with open('Lesson_1_task_2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)
