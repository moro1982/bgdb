FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y apache2 apache2-dev && \
    apt-get install -y libapache2-mod-wsgi-py3 && \
    apt-get clean

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN python3 -m venv /app/venv  # Crea el entorno virtual en /app/venv
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt  # Instala las dependencias en el entorno virtual

COPY . /app

RUN a2enmod wsgi

COPY apache-flask.conf /etc/apache2/sites-available/000-default.conf

EXPOSE 80

CMD ["apache2ctl", "-D", "FOREGROUND"]