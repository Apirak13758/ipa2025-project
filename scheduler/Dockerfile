FROM python:3.10-slim
WORKDIR /home/myapp
COPY requirements.txt .
COPY producer.py .
RUN pip install -r requirements.txt
EXPOSE 8080
CMD ["python3", "app.py"]
