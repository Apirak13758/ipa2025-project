FROM python:3.12.3
WORKDIR /home/myapp
COPY requirements.txt .
COPY db_handler.py .
COPY parser_handler.py .
COPY ssh_handler.py .
COPY worker.py .
COPY templates/ ./templates/
RUN pip install -r requirements.txt
CMD ["python", "worker.py"]
