# Dockerfile, Image, Container
FROM python:3.9.12
ENV WORKSPACE /opt/installs
RUN mkdir -p $WORKSPACE
WORKDIR $WORKSPACE
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY src .
CMD ["python3.9", "main.py"]