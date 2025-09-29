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


def produce(host, body):
    """
    Connect to RabbitMQ and publish a message.

    Args:
        host (str): The RabbitMQ server hostname.
        body (str): The message body to publish.
        exc_name (str): The name of the exchange.
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
        channel.exchange_declare(exchange="jobs", exchange_type="direct")
        channel.queue_declare(queue="router_jobs")
        channel.queue_bind(
            queue="router_jobs", exchange="jobs", routing_key="check_interfaces"
        )

        # Publish the message.
        channel.basic_publish(
            exchange="jobs", routing_key="check_interfaces", body=body
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
    host = "localhost"
    message_body = "192.168.1.44"
    produce(host, message_body)


# This construct makes the script reusable as a module.
if __name__ == "__main__":
    main()
