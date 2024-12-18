# Connector Diagnostics Module
#
# This file is part of the Audio Connector Getting Started repository.
# https://github.com/industrial-edge/audio-connector-getting-started
#
# MIT License
#
# Copyright (c) Siemens 2022
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

import json
import math
import time
import datetime
import threading
import numpy as np

APPNAME = 'DiagnosticsEngine'

class PacketDiagnostics(object):
    """Parent class for diagnostics engines."""

    # reporting parameters
    obj_name = "" # user-specified name for the diagnostics engine
    report_interval = 10 # seconds between consecutive reports
    last_report_time = None # time of last generated report
    report_data = {} # diagnostics to be included in the report

    # data payload parameters
    packet_rate = 1. # packets per second

    # diagnostics memory
    history_size = 10 # number of packets to store for analysis
    packet_history = [] # running list of the history_size most recent packets
    previous_packet_ts = None

    # system parameters
    num_devices = 0
    num_clients = 0 # number of clients connected

    # minimum and maximum time difference between consecutive packets
    min_packet_delay = None
    max_packet_delay = None
    key_min_packet_delay = "Minimum packet delay (s)"
    key_max_packet_delay = "Maximum packet delay (s)"

    # Total number of packets counted (i.e., received or sent) versus expected
    num_packets_counted = 0
    num_packets_expected = 0

    def __init__(self,name="DIAG",interval=10,history=10,packet_rate=1.):
        self.obj_name = name # user-specified name for the diagnostics engine
        self.report_interval = interval # seconds between consecutive reports
        self.history_size = history # number of packets to store for analysis
        self.packet_rate = packet_rate # packets per second
        self.reset(print_reset=False)

    def count_packet(self,ts=None):
        self.num_packets_counted += 1

        if self.previous_packet_ts is None:
            self.previous_packet_ts = ts
            return
        
        keys = self.report_data.keys()
        latest_packet_delay = (ts - self.previous_packet_ts).total_seconds()
        if self.key_min_packet_delay in keys and (self.min_packet_delay is None or latest_packet_delay < self.min_packet_delay):
            self.min_packet_delay = latest_packet_delay
        if self.key_max_packet_delay in keys and (self.max_packet_delay is None or latest_packet_delay > self.max_packet_delay):
            self.max_packet_delay = latest_packet_delay
        self.previous_packet_ts = ts

    def store_packet(self,packet,ts=None):
        # store raw packets; make no assumptions about payload structure
        new_packet = {'ts': ts, 'packet': packet}
        # print(f'{APPNAME}::[{self.obj_name}] packet received for diagnostics: '+str(new_packet),flush=True)

        self.packet_history.append(new_packet) # add the newest packet to history
        if len(self.packet_history) >= self.history_size:
            self.packet_history.pop(0) # remove the oldest one
        
        self.num_packets_counted += 1
        # print(f'{APPNAME}::[{self.obj_name}] new packet received, now counted: '+str(self.num_packets_counted),flush=True)
        self.analyze() # analyze packet history and update report data

    def analyze(self,keys=None):
        if keys is None:
            keys = self.report_data.keys()
        
        if len(self.packet_history) >= 2:
            latest_packet_delay = (self.packet_history[-1]['ts'] - self.packet_history[-2]['ts']).total_seconds()
            if self.key_min_packet_delay in keys and (self.min_packet_delay is None or latest_packet_delay < self.min_packet_delay):
                self.min_packet_delay = latest_packet_delay
            if self.key_max_packet_delay in keys and (self.max_packet_delay is None or latest_packet_delay > self.max_packet_delay):
                self.max_packet_delay = latest_packet_delay
    
    def reset(self,print_reset=True):
        self.num_packets_counted = 0
        self.packet_history = []
        self.last_report_time = datetime.datetime.now()
        self.previous_packet_ts = None
        self.min_packet_delay = None
        self.max_packet_delay = None
        if print_reset:
            print(f'{APPNAME}::[{self.obj_name}] Diagnostics statistics reset!',flush=True)

    def start_reporting(self):
        print(f'{APPNAME}::[{self.obj_name}] Starting diagnostics engine...',flush=True)
        self.reset(print_reset=False)                   # reset timer
        self.generate_report(print_report=False)        # initialize report_data
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.run_reporting, args=(self.stop_event, ))
        self.thread.daemon = True                            # Daemonize thread
        self.thread.start()                                  # Start the execution
    
    def stop_reporting(self):
        self.stop_event.set() # set stop flag

    def run_reporting(self, stop):
        while not stop.is_set():
            if self.last_report_time is None:
                self.generate_report()
            else:
                time_since_last_report = (datetime.datetime.now() - self.last_report_time).total_seconds()
                if time_since_last_report > self.report_interval:
                    self.generate_report(time_since_last_report)
                else:
                    time.sleep(self.report_interval - time_since_last_report)
    
    def generate_report(self,time_since_last_report=None,print_report=True):
        if time_since_last_report is None:
            self.num_packets_expected = -1
        else:
            self.num_packets_expected = math.floor(time_since_last_report * self.packet_rate)

        # populate report_data
        self.report_data["Diagnostics ID"] = self.obj_name
        self.report_data["Time since last report (s)"] = time_since_last_report
        self.report_data["Number of packets expected"] = self.num_packets_expected
        self.report_data["Number of packets counted"] = self.num_packets_counted
        self.report_data["Expected packet delay (s)"] = 1. / self.packet_rate
        self.report_data[self.key_min_packet_delay] = self.min_packet_delay
        self.report_data[self.key_max_packet_delay] = self.max_packet_delay

        # print the report & reset
        self.last_report_time = datetime.datetime.now()
        if print_report:
            print(f'{APPNAME}::[{self.obj_name}] Diagnostics Report -- {self.last_report_time}\n'+
                  json.dumps(self.report_data,indent=4),flush=True)
        self.reset(print_reset=False)

class AudioStreamDiagnostics(PacketDiagnostics):

    data_sampling_rate = 1. # samples per second
    packet_size = 1 # samples per packet

    def __init__(self,name="DIAG",interval=10,history=10,samp_rate=1.,buff_size=1):
        PacketDiagnostics.__init__(self, name=name, interval=interval, history=history,
            packet_rate = samp_rate / buff_size)
        self.data_sampling_rate = samp_rate # samples per second
        self.packet_size = buff_size # samples per packet
        self.reset(print_reset=False)

    def set_sampling_rate(self, samp_rate):
        self.data_sampling_rate = samp_rate # samples per second
        self.packet_rate = samp_rate / self.packet_size

    def set_packet_size(self, buff_size):
        self.packet_size = buff_size # samples per packet
        self.packet_rate = self.data_sampling_rate / buff_size
