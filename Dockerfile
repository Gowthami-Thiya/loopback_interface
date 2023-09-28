FROM python:3.10
COPY requirements.txt /
RUN apt-get update && apt-get install -y gcc python3-dev build-essential
RUN pip install -r /requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 5000
CMD [ "python", loopback.py]