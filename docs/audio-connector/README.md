# Audio Connector

The **Audio Connector** is one component of an ecosystem of Edge apps that enable acoustic data collection and analytics on Siemens Industrial Edge.

![Edge Ecosystem](images/connsuite-ecosystem.png)

As seen in this diagram, configuration and operation of the **Audio Connector** is dependent on several other components,
all of which are part of the **Industrial Information Hub (IIH)** on Siemens Industrial Edge.

## Installation

To install the **Audio Connector**, first you must purchase a license through the [IE Marketplace](https://www.dex.siemens.com/edge/manufacturing-process-industries)
or the [Industry Mall](https://mall.industry.siemens.com/mall/en/us/Catalog/Products/10364120).
Then, copy the app from your IE Hub into your IE Management Catalog.
You may now install the app as normal onto your Edge device.
Configuration of the app at this stage is optional;
if no configuration is provided, the **Audio Connector** will automatically generate a valid configuration for all detected audio devices.

Once installed, hardware access to any connected audio devices is implemented through the Linux-native `/dev/snd` volume:

![Hardware Access](images/hardware-access.png)

On the same Edge device, also install the **IIH Common Configurator**, the **IIH Registry Service**, and the **IIH Databus Gateway**.
This completes the installation of the **Audio Connector**; you are now ready to configure the app.

## Configuration

Configuration of the **Audio Connector** is handled through the **IIH Common Configurator**.

1. First, open the UI of the **IIH Common Configurator**:

![IIH Main Page](images/iih-connector-config.png)

2. Next, select the **Audio Connector**:

![IIH Audio Connector](images/iih-audio-connector.png)

3. If your audio device is not already shown, add it as a new datasource:

![IIH Add Connection](images/iih-data-source.png)

**Note**: all audio devices discovered by the **Audio Connector** will be listed in the `dev_log.json` file,
which can be downloaded from the app management page of the IED.
This list is updated upon restart of the **Audio Connector**.

4. Now, add tags to that connection:

![IIH Add Tag](images/iih-add-tag.png)

**Note**: device channels start at `0`.

5. Select the tags you which to configure for each audio device, and deploy:

![IIH Deploy Configuration](images/iih-deploy-tags.png)

### Databus Gateway Configuration

Now, to forward the configured data tags from the **Audio Connector** onto the **IE Databus**, we use the **IIH Databus Gateway**.
This can be performed either from the **IIH Common Configurator** via the "Publish to Databus" checkboxes,
or via direct configuration of the **IIH Databus Gateway** from your IEM.

An example **IIH Databus Gateway** configuration is shown below:
```json
{
  "configs":[
    {
      "$schema":"https://siemens.com/connectivity_suite/schemas/mqtt-gw/1.0.0/config.json",
      "config":{
        "parameters":{
          "mqtt_server_name":"ie-databus",
          "mqtt_client_id":"cs-mqtt-gateway",
          "user_name":"edge",
          "password":"edge",
          "pub_topic_metadata":"ie/m/j/simatic/v1/cs-mqtt-gtw/dp/r",
          "pub_topic_status":"ie/s/j/simatic/v1/cs-mqtt-gtw/status"
	      },
        "data_sources":[
          {
            "name":"Umik-1",
            "driver_instance":"csaudioconn",
            "connection_name":"Umik-1  Gain: 18dB: USB Audio (hw:3,0) at index 4",
            "parameters":{
              "request_cycle":85,
              "pub_topic_timeseries":  "ie/d/j/simatic/v1/csaudioconn/dp/r/audio-device-1",
              "subscr_topic_write_req":"ie/d/j/simatic/v1/csaudioconn/dp/w/audio-device-1",
              "pub_topic_write_rsp":   "ie/d/j/simatic/v1/csaudioconn/dp/w/audio-device-1/response",
              "pub_topic_read_rsp":    "ie/d/j/simatic/v1/csaudioconn/dp/r/audio-device-1/response",
              "subscr_topic_read_req": "ie/d/j/simatic/v1/csaudioconn/dp/r/audio-device-1/request"
            },
            "datapoints":[
              { "name":"ch0", "parameters": {"data_type":"Int"}}
            ]
          },
          {
            "name":"Scarlett",
            "driver_instance":"csaudioconn",
            "connection_name":"Scarlett 18i20 USB: Audio (hw:1,0) at index 2",
            "parameters":{
              "request_cycle":85,
              "pub_topic_timeseries":  "ie/d/j/simatic/v1/csaudioconn/dp/r/audio-device-2",
              "subscr_topic_write_req":"ie/d/j/simatic/v1/csaudioconn/dp/w/audio-device-2",
              "pub_topic_write_rsp":   "ie/d/j/simatic/v1/csaudioconn/dp/w/audio-device-2/response",
              "pub_topic_read_rsp":    "ie/d/j/simatic/v1/csaudioconn/dp/r/audio-device-2/response",
              "subscr_topic_read_req": "ie/d/j/simatic/v1/csaudioconn/dp/r/audio-device-2/request"
            },
            "datapoints":[
              { "name":"ch0", "parameters": {"data_type":"Int"}},
              { "name":"ch1", "parameters": {"data_type":"Int"}}
            ]
          }
        ]
      }
    }
  ]
}
```

Note that the `connection_name` fields must match those in the `audio-conn-config.json` of the **Audio Connector**, e.g.:

```json
{
    "configs": [
        {
            "$schema": "https://siemens.com/connectivity_suite/schemas/audio-connector/1.0.0/config.json",
            "config": {
                "connections": [
                    {
                        "parameters": {
                            "device_name": "Scarlett 18i20 USB: Audio (hw:1,0)",
                            "sampling_rate": 44100,
                            "frame_size": 4096,
                            "stream_format": "Int16"
                        },
                        "name": "Scarlett 18i20 USB: Audio (hw:1,0) at index 2",
                        "datapoints": [
                            {
                                "parameters": {},
                                "address": {
                                    "channel": 0
                                },
                                "name": "ch0",
                                "access_mode": "r",
                                "array_dimensions": [
                                    0
                                ],
                                "data_type": "Int"
                            },
                            {
                                "parameters": {},
                                "address": {
                                    "channel": 1
                                },
                                "name": "ch1",
                                "access_mode": "r",
                                "array_dimensions": [
                                    0
                                ],
                                "data_type": "Int"
                            }
                        ]
                    },
                    {
                        "parameters": {
                            "device_name": "Umik-1  Gain: 18dB: USB Audio (hw:3,0)",
                            "sampling_rate": 48000,
                            "frame_size": 4096,
                            "stream_format": "Int16"
                        },
                        "name": "Umik-1  Gain: 18dB: USB Audio (hw:3,0) at index 4",
                        "datapoints": [
                            {
                                "parameters": {},
                                "address": {
                                    "channel": 0
                                },
                                "name": "ch0",
                                "access_mode": "r",
                                "array_dimensions": [
                                    0
                                ],
                                "data_type": "Int"
                            },
                            {
                                "parameters": {},
                                "address": {
                                    "channel": 1
                                },
                                "name": "ch1",
                                "access_mode": "r",
                                "array_dimensions": [
                                    0
                                ],
                                "data_type": "Int"
                            }
                        ]
                    }
                ]
            }
        }
    ]
}
```

## Operation

To verify that the **Audio Connector** is functioning properly, we can use **IE Flow Creator** to monitor the traffic on the **IE Databus**:

![Flow Creator Databus](images/flow-creator-debug-databus.png)

Similarly, we can browse the connection metadata on the **IE Databus**:

![Flow Creator Metadata](images/flow-creator-debug-metadata.png)

To visualize the audio datastream as a real-time waveform, you can use the [Edge Oscilloscope](../edge-oscilloscope/README.md) app.

## Applications

Two example applications which consume the audio data generated by the **Audio Connector** on the **IE Databus**
(via the **IIH Databus Gateway**) are the **Edge Oscilloscope** and the **Audio Processor**.

### Edge Oscilloscope

The **Edge Oscilloscope** is an example application provided for free on Siemens Industry Online Support (SIOS).
Additional instructions can be found [here](../edge-oscilloscope/README.md).

### Audio Processor

The **Audio Processor** is an example application provided as open source in this repository.
Additional instructions can be found [here](../audio-processor/README.md).

## Resources

- [Audio Connector Manual](https://support.industry.siemens.com/cs/ww/en/view/109805476)
- [Common Configurator Manual](https://support.industry.siemens.com/cs/ww/en/view/109803582)
- [Edge Oscilloscope Download](https://support.industry.siemens.com/cs/us/en/view/109808369)
