FROM python:3.9-slim-buster
RUN apt-get update

# add python dependencies
COPY ./test/playback/requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt

# add additional files
ADD ./app/pkg /app/pkg

# run app
ENV PYTHONPATH "${PYTHONPATH}:/app/pkg/"
COPY ./test/playback/audio_playback.py /app/audio_playback.py
CMD python3 audio_playback.py