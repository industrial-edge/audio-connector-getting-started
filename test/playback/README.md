# Audio File Playback Test Program

This program emulates a data stream from an audio device, as if provided by the **Audio Connector**.
This playback program can be used to verify the data flow through the **Audio Processor**.

## Downloading an audio sample

To download a sample audio file, run the following the `./test/playback` directory of this repository:
```sh
mkdir -p data
curl --output data/piano2.wav https://www.kozco.com/tech/piano2.wav
```
This downloads a short, free audio sample to a file called `piano2.wav`.

## Build the application

To build the audio file playback docker image, simply run:
```sh
docker-compose build
```
Note that the audio file you wish to playback must already be in the `./test/playback/data` directory,
since it will be built into the docker image.

## Configuring the playback program

Configuration of the playback program is found [here](config/config.json):
```json
{
    "file_name": "piano2.wav",
    "frame_size": 4096,
    "databus": {
        "databus_host": "ie-databus",
        "databus_port": 1883,
        "databus_username": "edge",
        "databus_password": "edge",
        "metadata_qos": 1,
        "streaming_qos": 2,
        "metadata_topic": "ie/m/j/simatic/v1/cs-mqtt-gtw/dp/r",
        "streaming_topic": "ie/d/j/simatic/v1/cs-mqtt-gtw/dp/r"
    }
}
```
The playback `file_name` will be published as the `connection_name` on the `metadata_topic` of the databus.

Then, run the following script:
```sh
sh start-playback-test.sh
```
This builds and runs both the audio file playback program and the **Audio Processor** app.

## Acknowledgment

The `piano2.wav` sample file was obtained from: https://www.kozco.com/tech/soundtests.html
