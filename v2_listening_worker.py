"""
This program reads messages from RabbitMQ queues and processes them.
It listens to the queues continuously and handles incoming messages.

Author: Tanner Young
Date: 5/19/2024
"""
import pika
import sys
import struct
from datetime import datetime
from collections import deque

# Define a deque to hold recent readings for monitoring conditions
temperature_window = deque(maxlen=24)  # Window for one day (24 hours)

def temperature_callback(ch, method, properties, body):
    """Define behavior on getting a message from the temperature queue."""
    timestamp, temperature = struct.unpack('!df', body)
    timestamp_str = datetime.fromtimestamp(timestamp).strftime("%m/%d/%y %H:%M:%S")
    print(f" [x] Received from temperature queue: {timestamp_str} - Temperature: {temperature}°C")

    # Add the new temperature reading to the deque
    temperature_window.append(temperature)

    # Example condition: Check if the temperature fluctuation is significant
    if len(temperature_window) == temperature_window.maxlen:
        if max(temperature_window) - min(temperature_window) >= 10:
            print(" [!] Temperature fluctuation alert! The temperature changed by 10°C or more in the last 24 hours!")

    print(" [x] Done.")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    """Continuously listen for task messages on named queues."""
    hn = "localhost"

    try:
        # Create a blocking connection to the RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hn))
    except Exception as e:
        print()
        print("ERROR: connection to RabbitMQ server failed.")
        print(f"Verify the server is running on host={hn}.")
        print(f"The error says: {e}")
        print()
        sys.exit(1)

    try:
        # Use the connection to create a communication channel
        channel = connection.channel()

        # Declare the queue
        queue_name = "hourly-temperature"
        channel.queue_delete(queue=queue_name)
        channel.queue_declare(queue=queue_name, durable=True)

        # Set the prefetch count to limit the number of messages being processed concurrently
        channel.basic_qos(prefetch_count=1)

        # Configure the channel to listen on the queue with the corresponding callback function
        channel.basic_consume(queue=queue_name, on_message_callback=temperature_callback, auto_ack=False)

        # Print a message to the console for the user
        print(" [*] Ready for work. To exit press CTRL+C")

        # Start consuming messages via the communication channel
        channel.start_consuming()

    except Exception as e:
        print()
        print("ERROR: something went wrong.")
        print(f"The error says: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print()
        print(" User interrupted continuous listening process.")
        sys.exit(0)
    finally:
        print("\nClosing connection. Goodbye.\n")
        connection.close()

if __name__ == "__main__":
    main()
