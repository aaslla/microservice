FROM python:3.8.11-alpine3.14

RUN apk add --no-cache \
    libressl-dev \
    musl-dev \
    libffi-dev \
    gcc

COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#RUN apk del \
#    libressl-dev \
#    musl-dev \
#    libffi-dev

#ENTRYPOINT [ "python" ]
#CMD ["application.py"]