FROM python:3.12

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

ENV GRADIO_SERVER_PORT=7861
ENV GRADIO_SERVER_NAME=0.0.0.0
EXPOSE 7861

CMD ["python", "app.py"]