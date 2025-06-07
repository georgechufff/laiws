# LAIWS - система ИИ-консультаций по юридическим вопросам

## Часть 1. О проекте</a>

LAIWS (от англ. Law AI Wide Search) - это интеллектуальный помощник, производящий консультации по правовым и нормативным вопросам.

## <a id="title2">Часть 2. Запуск приложения</a>
### Установка вручную

Для того, чтобы запустить приложение, необходимо скачать все зависимости из файла ```requirements.txt```.

Windows:
```
$ python3 -m venv .venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ gdown 1k0h3gv4GF1emsu7RTpLt2aKjUbZdNBuL
$ tar -xf faiss_index.zip
```

Linux:
```
$ python3 -m venv .venv
$ venv\Scripts\activate.bat
$ pip install -r requirements.txt
$ gdown 1k0h3gv4GF1emsu7RTpLt2aKjUbZdNBuL
$ unzip faiss_index.zip
```

Затем запустите файл main.py. 
```
$ streamlit run main.py
```

### Установка через Docker Compose

Если на вашем компьютере установлен Docker и Docker Compose, то запустите приложение следующей командой

```
$ docker compose up
```


