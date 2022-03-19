FROM bitnami/spark:3
USER 0
RUN pip install pyspark
USER 1001
COPY late_consumer.py .
COPY mongo-spark-connector_2.12-3.0.1.jar ./jars
COPY mongo-java-driver-3.12.10.jar ./jars
CMD ["spark-submit", "late_consumer.py"]
