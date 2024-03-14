FROM python:3.6-stretch

MAINTAINER Ilya Sychev "ilya.sychev@tu-dresden.de"

RUN apt-get -y --no-install-recommends install curl gnupg && curl -sL https://deb.nodesource.com/setup_12.x | bash - && apt-get update \
    && apt-get -y --no-install-recommends install nodejs git nginx supervisor

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

# Install python requirements
RUN pip3 install git+https://github.com/jhuapl-boss/boss-oidc.git && pip3 install -r requirements.txt \
    && pip3 install uwsgi

# Install node packages
COPY ./static /app/static
RUN cd /app/static && npm install

# Copy other sources
COPY ./templates /app/templates
COPY ./src /app/src

# Install uWSGI
RUN mkdir -p /etc/uwsgi && ln -sf /dev/stdout /var/log/nginx/access.log \
	&& ln -sf /dev/stderr /var/log/nginx/error.log

COPY docker/uwsgi.ini /etc/uwsgi/
COPY docker/nginx.conf /etc/nginx/
COPY docker/supervisord.conf /etc/supervisord.conf

# Custom Supervisord config

EXPOSE 80 443

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]