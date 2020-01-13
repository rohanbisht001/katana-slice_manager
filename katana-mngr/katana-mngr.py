from katana.utils.sliceUtils import sliceUtils

from kafka import KafkaConsumer, errors
import json
import time
import logging
import logging.handlers

# Logging Parameters
logger = logging.getLogger(__name__)
file_handler = logging.handlers.RotatingFileHandler(
    'katana.log', maxBytes=10000, backupCount=5)
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
stream_formatter = logging.Formatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(stream_formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Create the Kafka Consumer
tries = 3
exit = False
while not exit:
    try:
        consumer = KafkaConsumer(
            'slice',
            bootstrap_servers=['kafka:19092'],
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='my-group',
            value_deserializer=lambda m: json.loads(m.decode('ascii')))
    except errors.NoBrokersAvailable as KafkaError:
        if tries > 0:
            tries -= 1
            time.sleep(5)
            logger.debug("One try is gone!!")
        else:
            logger.error(KafkaError)
    else:
        logger.debug(tries)
        exit = True
        tries = 3

# Check for new messages
for message in consumer:
    logger.debug(message.value)
    action = message.value["action"]
    payload = message.value["message"]
    # Add slice
    if action == "add":
        sliceUtils.add_slice(payload)
    # Delete slice
    elif action == "delete":
        sliceUtils.delete_slice(payload)
