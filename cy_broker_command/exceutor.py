import pika

# Define connection parameters (adjust if needed)
connection_params = pika.ConnectionParameters(host='localhost')

# Connect to the RabbitMQ server
connection = pika.BlockingConnection(connection_params)

# Create a channel
channel = connection.channel()

# Define the queue name (change if necessary)
queue_name = 'my_queue'

# Declare the queue if it doesn't exist already
channel.queue_declare(queue=queue_name)

# Define the message to send
message = "This is a test message!"

# Publish the message to the queue
channel.basic_publish(exchange='', routing_key=queue_name, body=message.encode())

print(f" [x] Sent '{message}'")

# Close the connection
connection.close()