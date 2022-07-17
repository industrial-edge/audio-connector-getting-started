ARG BUILD_IMG=python:3.10.4-slim-bullseye
ARG DEPLOY_IMG=debian:bullseye-20220418-slim

# build image
FROM ${BUILD_IMG}

# install OS dependencies
RUN apt-get update
RUN apt-get install -y apt-utils
RUN apt-get install -y gcc

# install python dependencies
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt

# copy source files
ADD ./pkg /app/pkg

# build executable
ENV LD_LIBRARY_PATH=/usr/local/lib
ENV PYTHONPATH "${PYTHONPATH}:/app/pkg/"
COPY ./audio_processor.py /app/audio_processor.py
RUN pyinstaller --path="/app/pkg/" -F ./audio_processor.py

# deployment image
FROM ${DEPLOY_IMG}

# run
WORKDIR /app
COPY --from=0 /app/dist /app/dist
ENV LD_LIBRARY_PATH=/usr/local/lib
ENTRYPOINT ["./dist/audio_processor", ""]