# Dockerfile, Image, Container
FROM python:3.8.10
WORKDIR /src
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY src .
CMD ["python3", "main.py"]