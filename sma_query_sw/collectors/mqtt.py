# -*- coding: utf-8 -*-

import argparse
import asyncio
import sys
import json
import ssl
import paho.mqtt.client as mqtt

from sma_query_sw.protocol import SMAClientProtocol
from sma_query_sw.settings import get_settings_from_file

import logging

_LOGGER = logging.getLogger(__name__)


parser = argparse.ArgumentParser(description="Launch SMA to MQTT Bridge")
parser.add_argument("--settings", required=False, help="Settings")

args = parser.parse_args()

mqtt_client = mqtt.Client()

settings = get_settings_from_file()

inverters = settings["inverters"]
mqtt_settings = settings["mqtt"]


async def collect_data(exiting):
    while not exiting.is_set():
        for address, inverter in inverters.items():
            inverter["protocol"].start_query()

            if "data" in inverter:
                output_data = json.dumps(inverter["data"])
                mqtt_client.publish(mqtt_settings.get("mqtt_topic", "solar/sma/{serial}/status")
                                    .format(serial=inverter["serial"]), output_data)
                if settings.get("stdout", False):
                    print(output_data)

        try:
            await asyncio.wait_for(exiting.wait(), settings.get("poll_interval", 60))
        except asyncio.TimeoutError:
            pass
        except KeyboardInterrupt:
            pass


async def shutdown(exiting):
    exiting.set()
    mqtt_client.loop_stop()

    for address, inverter in inverters.items():
        await inverter["transport"].close()

    sys.exit(0)


async def main():
    if "ca_certs" in mqtt_settings:
        mqtt_client.tls_set(ca_certs=mqtt_settings.get("ca_certs", None),
                            tls_version=ssl.PROTOCOL_TLSv1_2, cert_reqs=ssl.CERT_NONE)

    mqtt_client.username_pw_set(mqtt_settings.get("mqtt_username", None), mqtt_settings.get("mqtt_password", None))

    mqtt_client.connect_async(mqtt_settings["mqtt_host"], port=mqtt_settings.get("mqtt_port", 1883),
                              keepalive=mqtt_settings.get("mqtt_keepalive", 60))

    mqtt_client.loop_start()

    loop = asyncio.get_running_loop()
    on_connection_lost = loop.create_future()
    exiting = asyncio.Event(loop=loop)

    for address, inverter in inverters.items():
        inverter["transport"], inverter["protocol"] = await loop.create_datagram_endpoint(
            lambda: SMAClientProtocol(inverter, on_connection_lost), remote_addr=(address, inverter.get("port", 9522)))

    loop.create_task(collect_data(exiting))

    try:
        await on_connection_lost
    except KeyboardInterrupt:
        pass
    finally:
        await shutdown(exiting)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

