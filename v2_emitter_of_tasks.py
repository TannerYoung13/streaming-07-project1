"""
This program reads temperature data generated using Faker.
The temperature is read at the top of each hour.

"""
import pika
import sys
import webbrowser
import struct
from datetime import datetime, timedelta
import time
import random
import faker

def offer_rabbitmq_admin_site():
    """Offer to open the RabbitMQ Admin website"""
    ans = input("Would you like to monitor RabbitMQ queues? y or n ")
    print()
    if ans.lower() == "y":
        webbrowser.open_new("http://localhost:15672/")
        print()

def send_message(host: str, queue_name: str, message: bytes):
    """
    Creates and sends a binary message to the specified queue.

    Parameters:
        host (str): the host name or IP address of the RabbitMQ server
        queue_name (str): the name of the queue
        message (bytes): the binary message to be sent to the queue
    """
    try:
        # create a blocking connection to the RabbitMQ server
        conn = pika.BlockingConnection(pika.ConnectionParameters(host))
        # use the connection to create a communication channel
        ch = conn.channel()
        # use the channel to declare a durable queue
        ch.queue_declare(queue=queue_name, durable=True)
        # use the channel to publish a message to the queue
        ch.basic_publish(exchange="", routing_key=queue_name, body=message)
        # print a message to the console for the user
        print(f" [x] Sent message to {queue_name}")
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error: Connection to RabbitMQ server failed: {e}")
        sys.exit(1)
    finally:
        # close the connection to the server
        conn.close()

def generate_hourly_temperatures():
    """Generate temperature data for each hour"""
    fake = faker.Faker()
    hourly_temperatures = []
    base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    for hour in range(24):
        timestamp = base_date + timedelta(hours=hour)
        temperature = round(random.uniform(-10, 35), 2)  # Random temperature in Celsius
        hourly_temperatures.append({
            'timestamp': timestamp,
            'temperature': temperature,
        })

    return hourly_temperatures

def main():
    """Generate temperature data and send it to RabbitMQ queues."""
    temperatures = generate_hourly_temperatures()
    
    for entry in temperatures:
        timestamp = entry['timestamp'].timestamp()
        temperature = entry['temperature']

        message = struct.pack('!df', timestamp, temperature)
        send_message("localhost", "hourly-temperature", message)
        
        # Sleep for a short time before sending the next message
        time.sleep(1)

# Standard Python idiom to indicate main program entry point
if __name__ == "__main__":  
    offer_rabbitmq_admin_site()
    main()
