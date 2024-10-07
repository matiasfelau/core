#!/bin/bash


until nc -z -v -w30 rabbitmq 5672
do
  echo "Esperando a que RabbitMQ esté disponible..."
  sleep 5
done

echo "RabbitMQ está disponible. Iniciando la aplicación..."