"""
A simple RabbitMQ producer script.

This script connects to a RabbitMQ instance, declares an exchange and a queue,
binds them, and publishes a message.
"""

import os
import pika

# It's a best practice to define module-level constants in uppercase.
RABBIT_USERNAME = os.getenv("RABBIT_USERNAME")
RABBIT_PASSWORD = os.getenv("RABBIT_PASSWORD")


def produce(host, body, exchange_name, queue_name, routing_key):
    """
    Connect to RabbitMQ and publish a message.

    Args:
        host (str): The RabbitMQ server hostname.
        body (str): The message body to publish.
        exchange_name (str): The name of the exchange.
        queue_name (str): The name of the queue.
        routing_key (str): The routing key for the message.
    """
    try:
        # Use more descriptive variable names for clarity.
        credentials = pika.PlainCredentials(RABBIT_USERNAME, RABBIT_PASSWORD)
        parameters = pika.ConnectionParameters(host, credentials=credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Declare the exchange and queue.
        channel.exchange_declare(
            exchange=exchange_name, exchange_type="direct"
        )
        channel.queue_declare(queue=queue_name)
        channel.queue_bind(
            queue=queue_name, exchange=exchange_name, routing_key=routing_key
        )

        # Publish the message.
        channel.basic_publish(
            exchange=exchange_name, routing_key=routing_key, body=body
        )

        print(f" [x] Sent '{body}'")

    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error: Could not connect to RabbitMQ. {e}")
    finally:
        # Ensure the connection is closed even if errors occur.
        if "connection" in locals() and connection.is_open:
            connection.close()


def main():
    """Main function to run the producer."""
    # Encapsulate the script's logic in a main function.
    host = "rabbitmq"
    message_body = "192.168.1.44"
    exchange = "jobs"
    queue = "router_jobs"
    key = "check_interfaces"
    produce(host, message_body, exchange, queue, key)


# This construct makes the script reusable as a module.
if __name__ == "__main__":
    main()
