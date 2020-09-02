import csv
import time
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path

import numpy as np


class MockupCNNPipeline:
    def __init__(self, data_path):
        self.dataset = {}
        with open(Path(data_path) / Path('dataset.tsv')) as fd:
            rd = csv.reader(fd, delimiter="\t", quotechar='"')
            for row in rd:
                self.dataset[row[2]] = {"ts": row[0], "source": row[1], "data": row[2]}
        def _load_matched(path):
            filename = Path(path).name
            entry = self.dataset.get(filename, None)
            if entry is not None:
                entry["data"] = np.load(path)
                return entry

        with ThreadPoolExecutor(max_workers=100) as pool:
            self.frames = list(sorted(pool.map(_load_matched, Path(data_path).glob('*.npy')), key=lambda item: item['ts']))

        self.started = None
        self.current_index = 0

    def get_available_data_packets(self):
        if self.started is None:
            self.started = time.time()
            return []

        to_return = []
        for index, item in enumerate(self.frames[self.current_index:]):
            if float(item['ts']) < time.time() - self.started:
                to_return.append(item['data'])
            else:
                self.current_index = self.current_index + index
                return to_return
        return to_return

    def get_available_nnet_and_data_packets(self):
        pass

if __name__ == "__main__":
    MockupCNNPipeline("data")