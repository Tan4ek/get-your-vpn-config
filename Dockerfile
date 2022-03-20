FROM python:3.8-buster
COPY . /app
WORKDIR /app
EXPOSE 8080/tcp
RUN pip install -r requirements.txt
CMD ["python3", "main.py"]