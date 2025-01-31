import threading
import carla
import pika

import sys
from pathlib import Path
sys.path.append(f'{Path(__file__).parent.parent}/resources')

from environments import carla_host, carla_port
from environments import mq_host, mq_port

def push_data(data, channel):
    channel.basic_publish(exchange='', routing_key='obstacle_distance', body=str(data.distance))

# Connect to CARLA server
client = carla.Client(carla_host, carla_port)
world = client.get_world()
world.wait_for_tick()
main_camera = world.get_actors().filter('sensor.camera.*')[0]

# Connect to the message queue
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=mq_host,
    port=mq_port))
channel = connection.channel()
channel.queue_declare(queue='obstacle_distance')
channel.confirm_delivery()

# Set up the sensors
blueprint = world.get_blueprint_library().find('sensor.other.obstacle')
transform = carla.Transform(carla.Location(x=0, y=0, z=0))
sensor = world.spawn_actor(blueprint, transform, attach_to=main_camera)
sensor.listen(lambda data: push_data(data, channel))

# Run until stopped
forever = threading.Event()
forever.wait()
