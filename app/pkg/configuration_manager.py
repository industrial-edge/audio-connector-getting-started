# Configuration Manager Module
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
import json
import datetime

APPNAME = 'ConfigurationManager'

def last_changed(fpath):
    return os.stat(fpath)[8]

class ConfigurationManager():
    """Configuration Manager class for apps configured via a config.json file."""

    def __init__(self,filepath=None):
        """Initialize Configuration Manager object."""
        if filepath is not None:
            self.set_config_path(filepath)
            self.load_config()
            self.update_mod_date()
        else:
            self.clear_config()

    def clear_config(self):
        """Reset App Configuration Manager data."""
        print(f'{APPNAME}::[CONFIG] all app config data cleared!', flush=True)
        self.config_path = None
        self.config_data = {}
        self.config_moddate = None

    def get_config_path(self):
        """Return path to config.json file."""
        return self.config_path
    
    def set_config_path(self,path):
        """Update path to config.json file."""
        self.config_path = path
    
    def get_config_data(self):
        """Return configuration data as dict."""
        return self.config_data
    
    def set_config_data(self,data):
        """Update configuration data dict."""
        self.config_data = data

    def update_mod_date(self):
        """Update internal timestamp when the config.json file was last modified."""
        self.config_moddate = last_changed(self.config_path)

    def check_changes(self,data=None):
        """Returns True if the config.json file has been modified; updates internal configuration data."""
        if last_changed(self.config_path) != self.config_moddate:
            self.load_config()
            self.update_mod_date()
            return True
        else:
            return False

    def create_backup(self,ts_string=None):
        """Create timestamped backup of config.json file."""
        if ts_string is None:
            ts_string = datetime.datetime.fromtimestamp(self.config_moddate).isoformat()
        file_name, file_ext = os.path.splitext(self.config_path)
        if file_ext == '':
            file_ext = '.json'
        out_path = f'{file_name}_{ts_string}{file_ext}'
        self.write_config(out_path)
        print(f'{APPNAME}::[CONFIG] previous config file backed up as {out_path}', flush=True)
        return out_path

    def load_config(self,in_path=None):
        """Load configuration data as dict from config.json file."""
        if in_path is None and self.config_path is None:
            print('Error - no config file path specified!')
            return
        elif in_path is None:
            in_path = self.config_path
        
        # load config file
        with open(in_path) as f:
            self.config_data = json.load(f)
            print(f'{APPNAME}::[CONFIG] loaded config file from {in_path}', flush=True)

    def write_config(self,out_path=None):
        """Write configuration data dict into config.json file."""
        if out_path is None and self.config_path is None:
            print(f'{APPNAME}::[CONFIG] Error - no config file path specified!')
            return
        elif out_path is None:
            out_path = self.config_path

        # write new config
        with open(out_path, 'w') as f:
            json.dump(self.config_data, f, indent=4)
        self.update_mod_date()


class MetadataManager(object):
    """Class for managing connection metadata."""
    def __init__(self,config_mgr):
        self.current = {
            "connection_name":"",
            "device_name":"",
            "sampling_rate":[1.],
            "num_chan":1,
            "data_type":[""],
            "streaming_topic":"",
        }
        self.previous = self.current.copy()
        self.config_mgr = config_mgr

        # populated by unpacking metadata topic's payload
        self.full_metadata = {}
        self.available_connections = []
        self.available_datapoints = []

    def set_connection(self,connection_name):
        try:
            conn_indx = self.available_connections.index(connection_name)
        except ValueError:
            print(f'{APPNAME}::[METADATA] Error: connection {connection_name} could not be found.')
            return False
            
        # NOTE: takes only the first timeseries datapoint set (available_datapoints[conn_indx][0])
        conn_dpts = self.available_datapoints[conn_indx][0]

        sampling_rate_list = [float(dpt_def["sampleRateHz"]) for dpt_def in conn_dpts["dataPointDefinitions"]]
        data_type_list = [dpt_def["dataType"] for dpt_def in conn_dpts["dataPointDefinitions"]]
        metadata_dict = {
            "connection_name":connection_name,
            "device_name":connection_name, # TODO: device name
            "sampling_rate":sampling_rate_list,
            "num_chan":len(conn_dpts["dataPointDefinitions"]),
            "data_type":data_type_list,
            "streaming_topic":conn_dpts["topic"]
        }
        self.update(metadata_dict)
        return True

    def update(self,input:dict):
        self.previous = self.current.copy()
        for k,v in input.items():
            if k in self.current.keys():
                self.current[k]=v
            else:
                print(f'{APPNAME}::[METADATA] Ignored additional param: {str(k)} = {str(v)}')
        return (self.current != self.previous)
    
    def update_metadata_objects(self, unpacked_metadata):
        full_metadata = unpacked_metadata[0]
        available_connections = unpacked_metadata[1]
        available_datapoints = unpacked_metadata[2]
        change_flag = False
        self.full_metadata = full_metadata # seq will always change
        if self.available_connections != available_connections:
            self.available_connections = available_connections
            change_flag = True
        if self.available_datapoints != available_datapoints:
            self.available_datapoints = available_datapoints
            change_flag = True
        return change_flag
