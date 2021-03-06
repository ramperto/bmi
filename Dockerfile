FROM python:3.8-slim-buster

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install 'uvicorn[standard]'

EXPOSE 3000

CMD ["python", "main.py"]