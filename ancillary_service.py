import os
import json
import ast
from datetime import timedelta
from celery import Celery

from typing import Dict, List
from redis_client import RedisConnection
from my_logger import MyLogger


redisClient = RedisConnection()
logger = MyLogger()

app = Celery("ancillary_service", broker="pyamqp://guest@localhost//")


@app.task
def process_data_packets(message: str) -> Dict:
    """Process the data packets from the celery task.

    Args:
        message (str): message is json string

    Returns:
        Dict: Returns the status of the processed message.
    """
    try:
        packet = json.loads(message)
        set_res_packet(packet)
        packet_handler(packet)
        return {"status": "processed"}
    except Exception as e:
        logger.info(f"Exceptions occurred while processing packets with error : {e}")
        return {"status": "failed"}


def set_res_packet(packet: Dict):
    """set the packet's data for each resource in redis

    Args:
        packet (Dict): Packet is json that contains the message with resource id
    """
    redisClient.zadd(
        packet.get("resource_id"),
        {
            calculate_words_from_packets(packet.get("payload")): packet.get(
                "packet_index"
            )
        },
    )


def get_all_res_packets(resource_id: int) -> List:
    """Fetch all list of integers for the particular resource from redis.

    Args:
        resource_id (int): resource id of data packet.

    Returns:
        List: List of integers for the particular resource.
    """
    return redisClient.zrange(resource_id, 0, -1, withscores=False)


def packet_handler(packet: Dict):
    """process the packet's data.

    Args:
        packet (Dict): Packet is json that contains the message with resource id.
    """
    res_packets_output = get_all_res_packets(packet.get("resource_id"))
    if packet.get("last_chunk"):
        process_last_packet(
            packet.get("resource_id"), res_packets_output, packet.get("packet_index")
        )
    else:
        process_missing_packets(packet.get("resource_id"), res_packets_output)


def calculate_words_from_packets(payload: str) -> str:
    """Calculate length of each words from payload.

    Args:
        payload (str): payload contains the message of data packet

    Returns:
        str: Returns the string of list of integers
             that contains the length of each word
    """
    li = [str(len(i)) for i in payload.split(" ")]
    return str(li)


def process_last_packet(
    resource_id: int, res_packets_output: List, last_packet_index: int
):
    """Process all the packets and send for downstreaming if received packet is the last chunk
       else set the last index number in redis for particular resource.

    Args:
        resource_id (int): Resource id of data packet.
        res_packets_output (List): It constains the list of integers.
        last_packet_index (int): Last index of resource
    """
    if last_packet_index == (len(res_packets_output) - 1):
        logger.info(f"All topics received for the resource id {resource_id}")
        logger.info(res_packets_output)
        downstream_webhook(resource_id, res_packets_output)
    else:
        logger.info(
            f"Last topic received for the resource id {resource_id} but few topics are missing"
        )
        redisClient.setex(
            "resource_last_index:" + str(resource_id),
            timedelta(seconds=65),
            value=last_packet_index,
        )


def process_missing_packets(resource_id: int, res_packets_output: List):
    """Process the missing packets that receives after last chunk.

    Args:
        resource_id (int): Resource id of data packet.
        res_packets_output (List): It constains the list of integers.
    """
    last_index = redisClient.get("resource_last_index:" + str(resource_id))
    logger.info(
        f"resource_last_index : {last_index}, length: {len(res_packets_output)}"
    )
    if last_index and int(last_index.decode("UTF-8")) == (len(res_packets_output) - 1):
        logger.info(
            f"sending for downstreaming the missing packets for the resource id {resource_id}"
        )
        logger.info(res_packets_output)
        downstream_webhook(resource_id, res_packets_output)


def downstream_webhook(resource_id: int, res_packets_output: List):
    """Write the list of integers per line in the file.

    Args:
        resource_id (int): Resource id of data packet.
        res_packets_output (List): It constains the list of integers.
    """
    final_output = []
    for li in res_packets_output:
        final_output = final_output + ast.literal_eval(li.decode("UTF-8"))
    folder_name = "resources/"
    os.makedirs(folder_name, exist_ok=True)
    file_path = folder_name + str(resource_id) + ".txt"
    with open(file_path, "w") as file:
        file.writelines(s + "\n" for s in final_output)
