FROM apache/spark-py:v3.3.1

USER root

WORKDIR /app

RUN apt-get update && \
    apt-get install -y unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY kaggle.json /root/.kaggle/kaggle.json
RUN chmod 600 /root/.kaggle/kaggle.json
RUN kaggle datasets download -d yasserh/nyc-taxi-trip-duration 
RUN unzip /app/nyc-taxi-trip-duration.zip -d /app/data
COPY src/ /app/src

ENTRYPOINT ["python3", "src/etl.py"]
