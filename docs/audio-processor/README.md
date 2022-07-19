# Audio Processor Example

## Build the application

### Clone the repository

- Clone or Download the source code repository to your engineering VM, e.g.:
```
git clone git@github.com:industrial-edge/audio-connector-getting-started.git
```

### Build the docker image

To build the **Audio Processor** docker image:

- Open console in the source code folder `cd ./app`
- Use command `docker-compose build` to create the docker image.
- This docker image can now be used to build you app with the Industrial Edge App Publisher
- *docker images | grep audio_processor* can be used to check for the images
- You should get a result similiar to this:

![Docker Build Result](images/docker-build.png)

## Upload App to the Industrial Edge Managment

Please find below a short description how to publish your application in your IEM.

For more detailed information please see the section for [uploading apps to the IEM](https://github.com/industrial-edge/upload-app-to-iem).

### Connect your Industrial Edge App Publisher

- Connect your Industrial Edge App Publisher to your docker engine
- Connect your Industrial Edge App Publisher to your Industrial Edge Managment System

### Upload App using the Industrial Edge App Publisher

- Create a new application using the Industrial Publisher
- Add a new version
- Add a new configuration at `./config/` using this [config.json](../../app/config/config.json) as a template
- Import the [docker-compose](../../app/docker-compose.yml) file using the **Import YAML** button
- **Start Upload** to transfer the app to Industrial Edge Managment
- Further information about using the Industrial Edge App Publisher can be found in the [IE Hub](https://iehub.eu1.edge.siemens.cloud/documents/appPublisher/en/start.html)

## Deploy the App

### Configure the App

Configuration of the audio processor is specified in this [config.json](../../app/config/config.json) file:

```json
{
    "connection_name": "piano2.wav",
    "databus":{
        "databus_host": "ie-databus",
        "databus_port": 1883,
        "databus_username": "edge",
        "databus_password": "edge",
        "metadata_qos": 1,
        "streaming_qos": 2,
        "output_qos": 0,
        "metadata_topic": "ie/m/j/simatic/v1/cs-mqtt-gtw/dp/r",
        "output_topic": "ie/d/j/audio-processor/output"
    }
}
```

Add description of the configuration here:

### Verify operation

Add description here