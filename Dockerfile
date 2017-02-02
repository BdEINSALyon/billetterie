FROM alpine

EXPOSE 8000
RUN apk update

RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    rm -r /root/.cache

RUN apk add python3-dev postgresql-dev gcc musl-dev

WORKDIR /app

COPY requirements.txt /app
RUN pip3 install -r requirements.txt

COPY . /app
VOLUME /app/staticfiles

ENV DATABASE_URL postgres://postgresql:postgresql@db:5432/valet
RUN chmod +x /app/bash/run-prod.sh
CMD /app/bash/run-prod.sh
