FROM python:3.10.1-slim-buster

COPY requirements.txt requirements.txt

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY src/ src/

EXPOSE 50505

CMD exec gunicorn --bind :50505 --workers 2 --threads 1 --timeout 0 'src.app:create_app()'
