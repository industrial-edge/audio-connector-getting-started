# Audio Processor Application
#
# This file is part of the Audio Connector Getting Started repository.
# https://github.com/industrial-edge/audio-connector-getting-started
#
# MIT License
#
# Copyright (c) 2022 Siemens Aktiengesellschaft
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import json, time, datetime
import numpy as np
from paho.mqtt import client as mqttc
from pkg.configuration_manager import ConfigurationManager, MetadataManager
from pkg.audio_packing import unpack_payload, unpack_metadata
from pkg.conn_diagnostics import AudioStreamDiagnostics

APP_NAME = "AudioProcessor"
CONFIG_FILE = '/app/config/config.json'
CONFIG_DATA = {}
CONFIG_MANAGER = None
METADATA_MANAGER = None
DIAGNOSTICS_ENGINE = None
MQTT_CLIENT = mqttc.Client(client_id=APP_NAME)

#### define supporting mqtt client methods
def on_connect(client, userdata, flags, rc):
    if rc == 0: # 0 = connection successful
        print(f"{APP_NAME}::[DATABUS] connected to MQTT broker", flush=True)
        client.connected_flag = True  # set flag

        # resubscribe to all the topics in case of disconnection
        CONFIG_DATA = CONFIG_MANAGER.get_config_data() # make sure CONFIG_DATA is up to date

        # subscribe to metadata, wait for first message
        print(f'{APP_NAME}::[DATABUS] resubscribing to {CONFIG_DATA["databus"]["metadata_topic"]}', flush=True)
        client.subscribe(CONFIG_DATA["databus"]["metadata_topic"], qos=CONFIG_DATA["databus"]["metadata_qos"])
        
        if METADATA_MANAGER.current["streaming_topic"] != "":
            # also subscribe to streaming topic
            print(f'{APP_NAME}::[DATABUS] resubscribing to {METADATA_MANAGER.current["streaming_topic"]}', flush=True)
            client.subscribe(METADATA_MANAGER.current["streaming_topic"], qos=CONFIG_DATA["databus"]["streaming_qos"])

def on_disconnect(client, userdata, rc):
    print(f'{APP_NAME}::[DATABUS] on_disconnect() called', flush=True)
    client.connected_flag = False
    if rc != 0:
    #ERROR: unexpected broker disconection. Try to reconnect. Stop only if config file changes
        while True:
            try:
                client.reconnect()
                return
            except:
                #ERROR:broker not available. Keep trying
                continue        

def on_message(client, userdata, msg):

    # case 1: metadata message handling
    if msg.topic==CONFIG_DATA["databus"]["metadata_topic"]:
        # unpack metadata payload
        meta_changed = METADATA_MANAGER.update_metadata_objects(unpack_metadata(msg.payload)) # update internal objects

        # set connection from config; can only be done once we have parsed a metadata message (update_metadata_objects)
        if METADATA_MANAGER.current["connection_name"] != CONFIG_DATA["connection_name"]:
            METADATA_MANAGER.set_connection(CONFIG_DATA["connection_name"]) # this will also set the streaming_topic

        if meta_changed:
            print(f'{APP_NAME}::[METADATA] metadata changed at source, adapting...',flush=True)
            if METADATA_MANAGER.previous["streaming_topic"] != "":
                # unsubscribe from previous streaming topic
                print(f'{APP_NAME}::[STREAMING] unsubscribing from: {METADATA_MANAGER.previous["streaming_topic"]}',flush=True)
                client.unsubscribe(METADATA_MANAGER.previous["streaming_topic"])
            # subscribe to new streaming topic
            print(f'{APP_NAME}::[STREAMING] subscribing to: {METADATA_MANAGER.current["streaming_topic"]}',flush=True)
            client.subscribe(METADATA_MANAGER.current["streaming_topic"], qos=CONFIG_DATA["databus"]["streaming_qos"])

        # Update Diagnostics Engine if sampling_rate changed
        if DIAGNOSTICS_ENGINE.data_sampling_rate != METADATA_MANAGER.current["sampling_rate"][0]:
            DIAGNOSTICS_ENGINE.set_sampling_rate(METADATA_MANAGER.current["sampling_rate"][0])
            DIAGNOSTICS_ENGINE.reset() # reset statistics

    # case 2: stream payload handling
    elif msg.topic==METADATA_MANAGER.current["streaming_topic"]:
        # unpack payload
        msg_array, msg_timestamp, msg_array_shape = unpack_payload(msg.payload)

        # Update Diagnostics Engine if frame_size changed
        if DIAGNOSTICS_ENGINE.packet_size != msg_array_shape[0]:
            DIAGNOSTICS_ENGINE.set_packet_size(msg_array_shape[0])
            DIAGNOSTICS_ENGINE.reset() # reset statistics

        # Upload to Diagnostics Engine
        decimal_index = msg_timestamp.find('.')
        msg_ts = datetime.datetime.fromisoformat(msg_timestamp[:decimal_index+7]) # drop the 7th decimal place and/or the Z
        DIAGNOSTICS_ENGINE.store_packet(json.loads(msg.payload),ts=msg_ts)

        # analyze data frame and publish result
        data_packet = {
            "timestamp":msg_timestamp,
            "connection_name":METADATA_MANAGER.current["connection_name"],
            "streaming_topic":METADATA_MANAGER.current["streaming_topic"],
            "result":_compute_rms(msg_array[:,:METADATA_MANAGER.current["num_chan"]]).tolist()
        }
        client.publish(CONFIG_DATA["databus"]["output_topic"], json.dumps(data_packet), qos=CONFIG_DATA["databus"]["output_qos"])

    # otherwise: ignore all other topics
    else:
        return

def _compute_rms(buff,axis=0):
    return np.sqrt(np.mean(np.power(buff,2.0),axis))

if __name__ == "__main__":

    # load CONFIG_FILE if it exists
    if os.path.isfile(CONFIG_FILE):
        CONFIG_MANAGER = ConfigurationManager(CONFIG_FILE)
        CONFIG_DATA = CONFIG_MANAGER.get_config_data()
        METADATA_MANAGER = MetadataManager(CONFIG_MANAGER)
    else:
        time.sleep(10)
        exit(1)

    # configure MQTT client
    MQTT_CLIENT.on_connect = on_connect
    MQTT_CLIENT.on_disconnect = on_disconnect
    MQTT_CLIENT.on_message = on_message
    MQTT_CLIENT.username_pw_set(CONFIG_DATA["databus"]['databus_username'], CONFIG_DATA["databus"]['databus_password'])

    # start subscription
    MQTT_CLIENT.connect(CONFIG_DATA["databus"]['databus_host'])
    MQTT_CLIENT.subscribe(CONFIG_DATA["databus"]["metadata_topic"], qos=CONFIG_DATA["databus"]["metadata_qos"])
    if METADATA_MANAGER.current["streaming_topic"] != "":
        MQTT_CLIENT.subscribe(METADATA_MANAGER.current["streaming_topic"], qos=CONFIG_DATA["databus"]["streaming_qos"])
    print(f'{APP_NAME}::[DATABUS] MQTT client subscriptions created!', flush=True)

    # Start Diagnostics Engine
    DIAGNOSTICS_ENGINE = AudioStreamDiagnostics(name="DATABUS",interval=60,history=10,
                            samp_rate=METADATA_MANAGER.current["sampling_rate"][0])
    DIAGNOSTICS_ENGINE.start_reporting()

    # blocking call to hold the program here
    MQTT_CLIENT.loop_forever()
