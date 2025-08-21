FROM python:3.12.3
WORKDIR /home/myapp
COPY requirements.txt .
COPY producer.py .
COPY database.py .
COPY scheduler.py .
RUN pip install pymongo
RUN pip install pika
CMD ["python3", "scheduler.py"]
