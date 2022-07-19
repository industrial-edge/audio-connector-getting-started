# Getting Started with the Audio Connector for Siemens Industrial Edge

## Description

In this Getting Started guide, we provide instructions for setting up and using the [Audio Connector](docs/audio-connector/README.md),
as well as several auxiliary applications on Siemens Industrial Edge.
For example, we provide instructions here for using the [Edge Oscilloscope](docs/edge-oscilloscope/README.md) example application,
which is provided for free on Siemens Industry Online Support (SIOS).
Additionally, we provide as an open-source example in this repository an [Audio Processor](docs/audio-processor/README.md) application,
which can serve as a template for advanced users to develop their own custom audio analytics applications for Industrial Edge.

### Overview

The purpose of this repository is to provide a guide for new users of the **Audio Connector** on Siemens Industrial Edge.
The intent is to serve as a universal entrypoint for working with the **Audio Connector**, but to keep the content concise,
many details are ommitted here, so interested readers should refer to the [existing documentation](#documentation) elsewhere.

### General Task

In this tutorial, you will install, configure, and operate the **Audio Connector** and **Edge Oscilloscope** applications on your Edge Device.
Additionally, you will build and deploy the **Audio Processor** example app from the source code provided in this repository.

## Requirements

### Prerequisites

### Used Components

Linux applications:
* Industrial Edge App Publisher v1.6.3
* Docker Engine v20.10.16
* Docker Compose v1.29.2

Edge device:
* Siemens SIMATIC IPC227E (nanobox)
* Industrial Edge Device OS v1.5.0-21-amd64

Audio devices:
* [miniDSP UMIK-1](https://www.minidsp.com/products/acoustic-measurement/umik-1)
* [Focusrite Scarlett 18i20](https://focusrite.com/en/usb-audio-interface/scarlett/scarlett-18i20)

Edge apps:
* Audio Connector v1.0.0 (or greater)
* IE Databus v1.5.3 (or greater)
* IE Flow Creator v1.2.4 (or greater)
* IIH Common Configurator v1.3.0 (or greater)
* Databus Gateway v1.2.0 (or greater)
* Registry Service v1.2.0 (or greater)
* Edge Oscilloscope v1.0.0 (or greater)

![Edge Ecosystem](docs/audio-connector/images/connsuite-ecosystem.png)

## Installation

Installation steps are covered in the following guides:
1. [Install Audio Connector](docs/audio-connector/README.md#installation)
2. [Install Edge Oscilloscope](docs/edge-oscilloscope/README.md#installation)
3. [Build Audio Processor](docs/audio-processor/README.md#build-the-application)
4. [Install Audio Processor](docs/audio-processor/README.md#deploy-the-app)

## Configuration

Configuration instructions are provided in the following guides:
1. [Audio Connector Configuration](docs/audio-connector/README.md#configuration)
2. [Edge Oscilloscope Operation](docs/edge-oscilloscope/README.md#configuration)
3. [Verify Audio Processor Operation](docs/audio-processor/README.md#configure-the-app)

## Usage

Usage information is covered in the following guides:
1. [Audio Connector Operation](docs/audio-connector/README.md#operation)
2. [Edge Oscilloscope Operation](docs/edge-oscilloscope/README.md#operation)
3. [Verify Audio Processor Operation](docs/audio-processor/README.md#verify-operation)

## Documentation

You can find further documentation and help in the following links:

* [Industrial Edge Hub](https://iehub.eu1.edge.siemens.cloud/#/documentation)
* [Industrial Edge Forum](https://www.siemens.com/industrial-edge-forum)
* [Industrial Edge landing page](https://new.siemens.com/global/en/products/automation/topic-areas/industrial-edge/simatic-edge.html)
* [Industrial Edge GitHub page](https://github.com/industrial-edge)
* [Audio Connector Manual](https://support.industry.siemens.com/cs/ww/en/view/109805476)
* [Common Configurator Manual](https://support.industry.siemens.com/cs/ww/en/view/109803582)
* [Edge Oscilloscope Download](https://support.industry.siemens.com/cs/us/en/view/109808369)

## Contribution

Thank you for your interest in contributing.
Anybody is free to report bugs, unclear documentation, and other problems regarding this repository in the [Issues](https://github.com/industrial-edge/audio-connector-getting-started/issues) section.
Everybody is free to propose any changes to this repository using [Pull Requests](https://github.com/industrial-edge/audio-connector-getting-started/pulls).

## Licence and Legal Information

Please read the [Legal information](LICENSE.txt).
