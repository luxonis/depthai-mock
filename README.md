# Depthai-Mock

This tool allows you to record the packets produced by DepthAI device into your disk
and then play them back again as they would be produced normally - but without actually running the DepthAI

## Installation

```
python3 setup.py develop
```
## Usage

Having DepthAI connected, run
```
depthai_mock -s previewout
```

then, when `data` folder is there, you can unplug the DepthAI and run

```
cd depthai_mock
python3 test.py -p ../data
```