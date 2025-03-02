FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y apache2 apache2-dev && \
    apt-get install -y libapache2-mod-wsgi-py3 && \
    a2enmod wsgi && \
    apt-get clean

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt 

COPY . /app

COPY apache-flask.conf /etc/apache2/sites-available/000-default.conf

RUN a2ensite 000-default.conf && a2dissite default-ssl.conf 

EXPOSE 80

CMD ["apache2ctl", "-D", "FOREGROUND"]
