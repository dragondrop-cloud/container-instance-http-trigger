FROM python:3.11.3-alpine3.18
RUN apk --no-cache add curl sudo bash

# Install the Azure CLI within the container
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY src/ src/

EXPOSE 50505

CMD exec gunicorn --bind :50505 --workers 2 --threads 1 --timeout 0 'src.app:create_app()'
