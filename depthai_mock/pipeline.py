import csv
import json
import time
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path

import numpy as np


class MockupMetadata:
    def __init__(self, ts):
        self.ts = ts

    def getTimestamp(self):
        return self.ts


class MockupDataPacket:
    def __init__(self, stream_name, data, ts):
        self.stream_name = stream_name
        self.data = data
        self.metadata = MockupMetadata(ts)

    def getData(self):
        return self.data

    def getMetadata(self):
        return self.metadata


class MockupDetection(dict):
    __getattr__ = dict.get


class MockupCNNPacket:
    def __init__(self, data, ts):
        if isinstance(data, list):
            self.raw = False
            self.data = [MockupDetection(item) for item in data]
        elif isinstance(data, dict):
            self.raw = True
            self.data = data

        self.metadata = MockupMetadata(ts)

    def getDetectedObjects(self):
        if self.raw:
            raise RuntimeError('getDetectedObjects should be used only when ["NN_config"]["output_format"] is set to detection! https://docs.luxonis.com/api/#creating-blob-configuration-file')
        return self.data

    def get_tensor(self, name):
        if isinstance(name, int):
            return self.data[list(self.data.keys())[name]]
        else:
            return self.data[name]

    def getOutputsList(self):
        return list(self.data.values())

    def getOutputsDict(self):
        return self.data

    def __getitem__(self, name):
        return self.get_tensor(name)

    def getMetadata(self):
        return self.metadata


class MockupCNNPipeline:
    def __init__(self, data_path):
        self.dataset = {}
        with open(Path(data_path) / Path('dataset.tsv')) as fd:
            rd = csv.reader(fd, delimiter="\t", quotechar='"')
            for row in rd:
                self.dataset[row[2]] = {"ts": float(row[0]), "source": row[1], "data": row[2]}
        def _load_matched(path):
            filename = Path(path).name
            entry = self.dataset.get(filename, None)
            if entry is not None:
                if entry['source'] == "nnet":
                    with open(path) as fp:
                        return MockupCNNPacket(data=json.load(fp), ts=entry['ts'])
                else:
                    return MockupDataPacket(stream_name=entry['source'], data=np.load(path), ts=entry['ts'])

        with ThreadPoolExecutor(max_workers=100) as pool:
            self.frames = list(sorted(pool.map(_load_matched, Path(data_path).glob('*.npy')), key=lambda item: item.getMetadata().getTimestamp()))
            self.nnets = list(sorted(pool.map(_load_matched, Path(data_path).glob('*.json')), key=lambda item: item.getMetadata().getTimestamp()))

        self.started = None
        self.current_index_data = 0
        self.current_index_nnet = 0

    def _get_available_packets(self, array, index):
        if self.started is None:
            self.started = time.time()
            return [], 0

        if index + 1 == len(array):
            raise StopIteration()

        to_return = []
        for i, item in enumerate(array[index:]):
            if item.getMetadata().getTimestamp() < time.time() - self.started:
                to_return.append(item)
            else:
                index = index + i
                return to_return, index
        return to_return, index

    def get_available_data_packets(self):
        data, self.current_index_data = self._get_available_packets(self.frames, self.current_index_data)
        return data

    def get_available_nnet_and_data_packets(self):
        data = self.get_available_data_packets()
        nnets, self.current_index_nnet = self._get_available_packets(self.nnets, self.current_index_nnet)
        return nnets, data


if __name__ == "__main__":
    MockupCNNPipeline("data")