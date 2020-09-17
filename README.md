# Depthai-Mock

This tool allows you to record the packets produced by DepthAI device into your disk
and then play them back again as they would be produced normally - but without actually running the DepthAI

## Installation

```
python3 setup.py develop
```
## Usage

```
usage: depthai_mock [-h] [-nd] [-t TIME] [-ai] [-b BLOB] [-bc BLOB_CONFIG] [-p PATH] [-s STREAMS [STREAMS ...]]

optional arguments:
  -h, --help            show this help message and exit
  -nd, --no-display     Do not try display the incoming frames
  -t TIME, --time TIME  Limits the max time of the recording. Mandatory whenused with -nd (--no-display) option
  -ai, --enable-ai      Store also the nnet results
  -b BLOB, --blob BLOB  Path to nnet model .blob file
  -bc BLOB_CONFIG, --blob-config BLOB_CONFIG
                        Path to nnet model config .json file
  -p PATH, --path PATH  Path where to store the captured data
  -s STREAMS [STREAMS ...], --streams STREAMS [STREAMS ...]
                        Define which streams to enable Format: stream_name or stream_name,max_fps Example: -s metaout previewout Example: -s metaout previewout,10 depth_sipp,10
```

Having DepthAI connected, run
```
depthai_mock -s previewout
```

then, when `data` folder is there, you can unplug the DepthAI and run

```
cd depthai_mock
python3 test.py -p ../data
```