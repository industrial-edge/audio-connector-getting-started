# Audio Playback Test Program
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

# import the necessary packages
import datetime
import time
import wave
import numpy as np
from paho.mqtt import client as mqtt
from pkg.configuration_manager import ConfigurationManager
from pkg.audio_packing import pack_payload, pack_metadata
from pkg.conn_diagnostics import AudioStreamDiagnostics

INT_DATA_TYPES = {8: np.int8, 16: np.int16, 24: None, 32: np.int32}

def on_connect(client, userdata, flags, rc):
    # print(f"CONNACK received with code {rc}")
    if rc == 0:
        print("connected to MQTT broker", flush=True)
        client.connected_flag = True  # set flag
    else:
        print("Bad connection to MQTT broker, returned code=", rc, flush=True)

def on_disconnect(client, userdata, rc):
    print("on_disconnect() called", flush=True)
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

# main function for running standalone
def main():
    # load config file
    config_obj = ConfigurationManager('/app/config/config.json')
    config_data = config_obj.get_config_data()
    print('Wave File to load: '+config_data["file_name"],flush=True)
    AUDIO_FILEPATH = '/app/data/'+config_data["file_name"]
    with wave.open(AUDIO_FILEPATH, mode='rb') as audio_reader:
        samp_rate = audio_reader.getframerate()

    # Start MQTT client
    client = mqtt.Client(client_id="audio-playback")
    client.connected_flag = False  # set flag
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.username_pw_set(config_data[ "databus"]["databus_username"], config_data[ "databus"]["databus_password"])
    client.connect(config_data[ "databus"]["databus_host"], config_data[ "databus"]["databus_port"])
    client.loop_start()
    time.sleep(4)  # Wait for connection setup to complete
    print('Now connected to: '+config_data["databus"]["databus_host"]+
        ",\n\t metadata topic: "+config_data["databus"]["metadata_topic"]+
        ",\n\t streaming topic: "+config_data["databus"]["streaming_topic"], flush=True)

    # create empty buffer
    frame_len = config_data[ "frame_size"]
    data_buffer = np.zeros((frame_len,1))

    # Start Diagnostics Engine
    conn_diag = AudioStreamDiagnostics(name="PLAYBACK",
                                      interval=60,
                                      history=10,
                                      samp_rate=samp_rate,
                                      buff_size=frame_len)
    conn_diag.start_reporting()

    # the file is played in an endeless loop
    while True:
        with wave.open(AUDIO_FILEPATH, mode='rb') as audio_reader:
            samp_rate = audio_reader.getframerate()
            bit_depth = audio_reader.getsampwidth() * 8
            num_chan = audio_reader.getnchannels()
            if num_chan > 1:
                data_buffer = np.zeros((frame_len,num_chan))
            
            print("file samp freq detected: "+str(samp_rate), flush=True)
            frame_delay_sec = frame_len/samp_rate

            metadata_packet = pack_metadata(config_data["file_name"],
                                            samp_rate,
                                            num_chan,
                                            "Int"+str(bit_depth),
                                            config_data["databus"]["streaming_topic"])
            if client.connected_flag:
                client.publish(config_data["databus"]["metadata_topic"], metadata_packet, qos=config_data["databus"]["metadata_qos"])

            while True:
                # publish frame
                cycle_start_t = datetime.datetime.now()
                buffer_bytes = audio_reader.readframes(frame_len)
                if buffer_bytes is None or len(buffer_bytes)==0:
                    print('End of file reached, restarting...',flush=True)
                    # break at end of file
                    break
                
                timestamp = datetime.datetime.now()
                idata = np.frombuffer(buffer_bytes, dtype=INT_DATA_TYPES[bit_depth])
                data_buffer = idata.reshape([-1, num_chan])
                if data_buffer.shape[0] < frame_len:
                    # zero pad if needed
                    num_pad = frame_len-data_buffer.shape[0]
                    print("incomplete buffer - padding with "+str(num_pad)+" zeros", flush=True)
                    data_buffer = np.pad(data_buffer,((0, num_pad), (0, 0)))
                if client.connected_flag:
                    data_packet = pack_payload(data_buffer, timestamp.isoformat())
                    client.publish(config_data["databus"]["streaming_topic"], data_packet, qos=config_data["databus"]["streaming_qos"])
                    # print('Published '+str(data_buffer.shape[0])+' samples onto the databus',flush=True)

                    # Upload to Diagnostics Engine
                    conn_diag.store_packet(data_packet,ts=timestamp)

                # sleep rest of the cycle
                cycle_end = datetime.datetime.now()
                diff_sec = (cycle_end - cycle_start_t).total_seconds()
                if diff_sec < frame_delay_sec:
                    sleep_time = frame_delay_sec - diff_sec
                    time.sleep(sleep_time)
            
        print('Once more, from the top!',flush=True)
    client.disconnect()
    client.loop_stop()

if __name__ == "__main__":
    main()