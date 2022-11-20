FROM python:3.8.10
WORKDIR /src
COPY src/ .
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY run.sh run.sh
RUN chmod +x run.sh
CMD ["./run.sh"]