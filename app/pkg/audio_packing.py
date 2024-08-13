# Audio Packing Module
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
import base64
import numpy as np

# Crude emulation of dpMetadataSimaticV1 format
# from v1.2.2 of [Edge Databus Payload Specification](https://code.siemens.com/drehermi/edge-databus-payload)
def pack_metadata(device_name,sampling_rate,num_chan,data_type,streaming_topic):
    metadata = {
        "seq": 0,
        "connections":[
            {
                "name":device_name,
                "type":"Audio Device",
                "dataPoints":[
                    {
                        "name":device_name,
                        "topic":streaming_topic,
                        "publishType":"timeseries",
                        "dataPointDefinitions":_gen_datapoint_defs(sampling_rate,
                                                num_chan,
                                                data_type)
                    }
                ]
            }
        ]
    }
    return json.dumps(metadata)

def _gen_datapoint_defs(sampling_rate,num_chan,data_type):
    # extend scalars to num_chan length lists
    if not isinstance(sampling_rate,list):
        sampling_rate = [sampling_rate] * num_chan
    if not isinstance(data_type,list):
        data_type = [data_type] * num_chan
    
    # generate definition for each datapoint
    dpt_defs = []
    for indx in range(num_chan):
        dpt_def = {
            "name":"ch"+str(indx),
            "id":str(indx),
            "dataType":data_type[indx],
            "valueRank":1,
            "arrayDimensions":[0],
            "accessMode":"r",
            "acquisitionCycleInMs":85,
            "acquisitionMode":"CyclicOnContinuous",
            "sampleRateHz":sampling_rate[indx]
        }
        dpt_defs.append(dpt_def)
    return dpt_defs

# Following dpMetadataSimaticV1 format
# from v1.2.2 of [Edge Databus Payload Specification](https://code.siemens.com/drehermi/edge-databus-payload)
def unpack_metadata(metadata_msg):
    full_metadata = json.loads(metadata_msg)

    # fail fast if metadata payload has no connections
    if "connections" not in full_metadata.keys():
        return full_metadata, [], []

    # list all connection names
    available_connections = [conn["name"] for conn in full_metadata["connections"]]

    # list all timeseries datapoints per connection
    available_datapoints = []
    for conn in full_metadata["connections"]:
        if "dataPoints" not in conn.keys():
            # skip empty connections
            continue
        timeseries_dpts = [dpt for dpt in conn["dataPoints"] if dpt["publishType"]=="timeseries"]        
        available_datapoints.append(timeseries_dpts)

    return full_metadata, available_connections, available_datapoints

# Crude emulation of subDpValueSimaticV11TimeSeriesPayload format
# from v1.2.2 of [Edge Databus Payload Specification](https://code.siemens.com/drehermi/edge-databus-payload)
def pack_payload(array, timestamp, ids=None):
    """Packs an audio array + timestamp into json message for MQTT transmission.
    See also unpack_payload."""
    # print('Packing payload... '+str(array[:10,0].flatten()),flush=True)
    if ids is None: # assume 0,1,2,...
        ids = [*range(array.shape[1])]

    var_list = []
    for col in range(array.shape[1]):
        var_entry = {
            "id": ids[col],
            "qc": 3, # TODO: provide this
            "qx": 0, # TODO: what is this
            "ts": timestamp+"0Z", # keep as string; add 7th decimal place & Z
            # "val": base64.b64encode(array[:,col].flatten('C')).decode('utf-8')
            "val": array[:,col].flatten().tolist() # TODO: should be list of int16s
        }
        var_list.append(var_entry)
    buff_json = {
        "seq": 1, # TODO: increment this
        "mdHashVer": 1, # TODO: what is this
        "records": [{
            "rseq": 1, # TODO: increment this
            "ts": timestamp+"0Z", # add 7th decimal place & Z
            "vals": var_list
            }]
        }

    # print('Packed the payload! '+str(buff_json),flush=True)
    return json.dumps(buff_json)

# Following subDpValueSimaticV11TimeSeriesPayload format
# from v1.2.2 of [Edge Databus Payload Specification](https://code.siemens.com/drehermi/edge-databus-payload)
def unpack_payload(payload):
    """Unpacks a json message received via MQTT into an audio array + timestamp.
    See also pack_payload."""
    msg_dict = json.loads(payload)
    # print(f'Unpacking payload with {len(msg_dict["records"])} records...',flush=True)
    array_list = []
    ids_list = []
    rseq_list = []
    ts_list = []
    for payload_record in msg_dict["records"]: # loop through records
        array, ids, rseq, ts = _unpack_payload_record(payload_record)
        array_list.append(array)
        ids_list.append(ids)
        rseq_list.append(rseq)
        ts_list.append(ts)
    merged_array, merged_ids, sorted_rseq, sorted_ts = _merge_payload_records(array_list,ids_list,rseq_list,ts_list)
    # if len(array_list) > 1:
    #     merged_array, merged_ids, sorted_rseq, sorted_ts = _merge_payload_records(array_list,ids_list,rseq_list,ts_list)
    # else:
    #     merged_array = array_list[0]
    #     id_list = ids_list[0]
    #     sorted_ts = ts_list
    array_shape = merged_array.shape

    # print('Unpacked the payload! '+str(merged_array[:10,:]),flush=True)
    timestamp = sorted_ts[0]
    return merged_array, timestamp, array_shape

def _unpack_payload_record(payload_record):
    rseq = payload_record["rseq"]
    timestamp = payload_record["ts"]
    ids = []
    ch_list = []
    for ch in payload_record["vals"]: # loop over datapoints
        ids.append(ch["id"]) # each id is one column -- what about 2-D arrays?
        ch_list.append(np.reshape(np.array([ch["val"]]),(-1,1))) # TODO: should be list of int16s
    array = np.hstack(tuple(ch_list)) # TODO: each datapoint could have its own data type
    # print(f'Unpacked {array.shape[0]}x{array.shape[1]} data from record {rseq}: ids={ids}, data={array[:10,:]}',flush=True)
    return array, ids, rseq, timestamp

def _merge_payload_records(array_list,ids_list,rseq_list,ts_list):
    np_dtype = array_list[0].dtype # array data type
    sort_key = [jj for _, jj in sorted(zip(rseq_list, range(len(rseq_list))))] # to sort by rseq

    # collect set of unique datapoint IDs
    id_set = set()
    for ids in ids_list:
        id_set.update(ids)

    # build up signals one datapoint at a time
    ch_list = []
    for id in id_set: # loop over all datapoint ids
        ch_data_items = []
        for ii in range(len(rseq_list)):
            # now we are accessing record jj
            jj = sort_key[ii] # sorted index
            jj_array = array_list[jj]
            jj_ids = ids_list[jj] # datapoints contained in this record
            jj_len = jj_array.shape[0] # column length for this record
            if id in jj_ids:
                # if the record has that datapoint, add it to the output
                ch_data_items.append(np.reshape(jj_array[:,jj_ids.index(id)],(-1,1)))
            # else:
            #     # TODO: fill with zeros and continue
            #     ch_data_items.append(np.zeros((jj_len,1), dtype=np_dtype))
        if len(ch_data_items) > 1:
            ch_data = np.vstack(tuple(ch_data_items))
        else:
            ch_data = ch_data_items[0]
        ch_list.append(ch_data)
    merged_array = np.hstack(tuple(ch_list))

    return merged_array, list(id_set), [rseq_list[ii] for ii in sort_key], [ts_list[ii] for ii in sort_key]
