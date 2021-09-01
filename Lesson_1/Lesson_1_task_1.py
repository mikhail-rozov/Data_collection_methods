"""
1. Посмотреть документацию к API GitHub, разобраться, как вывести список репозиториев для конкретного пользователя,
сохранить JSON-вывод в файле *.json.
"""
import requests
import json

username = 'shkin29'
req = requests.get(f'https://api.github.com/users/{username}/repos')
data = json.loads(req.text)
with open('./Lesson_1_task_1.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)
