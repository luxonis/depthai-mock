import csv
import time
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path

import numpy as np


class MockupDataPacket:
    class MockupMetadata:
        def __init__(self, ts):
            self.ts = ts

        def getTimestamp(self):
            return self.ts

    def __init__(self, stream_name, data, ts):
        self.stream_name = stream_name
        self.data = data
        self.metadata = self.MockupMetadata(ts)

    def getData(self):
        return self.data

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
                return MockupDataPacket(stream_name=entry['source'], data=np.load(path), ts=entry['ts'])

        with ThreadPoolExecutor(max_workers=100) as pool:
            self.frames = list(sorted(pool.map(_load_matched, Path(data_path).glob('*.npy')), key=lambda item: item.getMetadata().getTimestamp()))

        self.started = None
        self.current_index = 0

    def get_available_data_packets(self):
        if self.started is None:
            self.started = time.time()
            return []

        if self.current_index + 1 == len(self.frames):
            raise StopIteration()

        to_return = []
        for index, item in enumerate(self.frames[self.current_index:]):
            if item.getMetadata().getTimestamp() < time.time() - self.started:
                to_return.append(item)
            else:
                self.current_index = self.current_index + index
                return to_return
        return to_return

    def get_available_nnet_and_data_packets(self):
        pass


if __name__ == "__main__":
    MockupCNNPipeline("data")