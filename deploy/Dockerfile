FROM python:3.7-stretch

RUN apt-get -y update && apt-get -y upgrade && apt-get install nginx git -y

RUN git clone --branch reprocess https://github.com/onsplatform/process_memory.git /var/www/memory

WORKDIR /var/www/memory

RUN pip install pipenv gunicorn
RUN pipenv install  --system --deploy


RUN cp /var/www/memory/deploy/memory.nginx /etc/nginx/sites-available/memory

RUN mkdir /var/log/memory \
 && rm -rf /etc/nginx/sites-enabled/default \
 && ln -s /etc/nginx/sites-available/memory /etc/nginx/sites-enabled/memory

ENV GUNICORN_TIMEOUT 3000
ENV PORT 9091
ENV HOST mongo
ENV DATABASE_NAME platform_memory

EXPOSE 9091

RUN cp /var/www/memory/deploy/docker_entrypoint.sh /docker_entrypoint.sh

RUN chmod +x /docker_entrypoint.sh

ENTRYPOINT ["sh", "/docker_entrypoint.sh"]
