FROM python:3.11-slim
LABEL authors="sergejporohov"

WORKDIR /app

COPY main.py /app/main.py
COPY requirements.txt requirements.txt
RUN pip install --upgrade setuptools
RUN pip3 install -r requirements.txt
RUN chmod 755 .

COPY . /app

CMD ["python", "app.py"]