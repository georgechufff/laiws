FROM python:3.10-slim

WORKDIR /usr/src
RUN pip install uv
COPY requirements.txt .
RUN uv pip install -r requirements.txt --system
COPY . .
EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"

CMD ["python", "app.py"]