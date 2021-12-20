# Rhea

Rhea is an open source package that is used for real-time stream processing simulation. It is built on top of the following open source tools:
- [RabbitMQ](https://www.rabbitmq.com/) - Message Broker
- [Apache Spark Streaming](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html) - Live Streaming Processing System
- [MongoDB Timeseries](https://docs.mongodb.com/manual/core/timeseries-collections/) - Timeseries Database
- [Grafana](https://grafana.com/) - Presentation Layer

## Description
This package is a product of a semester project whose purpose was to create a prototype of a real IoT system. This project consists of multiple sensors sending virtual real-time data to an MQTT broker that then get transformed to daily data using Apache Spark Streaming. Consequently the transformed data are stored in a NoSQL time-series database and are presented using Grafana.


## Steps
1. Send virtual data to the message layer
2. Process and transform data
3. Store in a database
4. Create a dashboard

## Creators
Zevgolatakos Panos [@panoszvg](https://github.com/panoszvg)

Papaioannou Konstantinos [@kon-pap](https://github.com/kon-pap)