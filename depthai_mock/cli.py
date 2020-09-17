import json

def _stream_type(option):
    option_list = option.split(",")
    if len(option_list) > 2:
        raise ValueError(f"{option} format is invalid.")

    stream_name = option_list[0]
    if len(option_list) == 1:
        stream_dict = {"name": stream_name}
    else:
        try:
            max_fps = float(option_list[1])
        except ValueError:
            raise ValueError(f"In option: {option} {option_list[1]} is not a number!")

        stream_dict = {"name": stream_name, "max_fps": max_fps}
    return stream_dict

def record_depthai_mockups():
    import argparse
    import depthai
    import time
    import cv2
    import csv
    import numpy as np
    from pathlib import Path
    from concurrent.futures.thread import ThreadPoolExecutor

    def __get_fullpath(path):
        return str((Path(__file__).parent / Path(path)).resolve().absolute())

    parser = argparse.ArgumentParser()
    parser.add_argument('-nd', '--no-display', dest="nodisplay", action='store_true', default=False, help="Do not try display the incoming frames")
    parser.add_argument('-t', '--time', type=int, default=-1, help="Limits the max time of the recording. Mandatory when"
                                                                   "used with -nd (--no-display) option")
    parser.add_argument('-ai', '--enable-ai', dest="ai", action='store_true', default=False, help="Store also the nnet results")
    parser.add_argument('-b', '--blob', default=(__get_fullpath('./mobilenet-ssd/mobilenet-ssd.blob')), type=str, help="Path to nnet model .blob file")
    parser.add_argument('-bc', '--blob-config', dest="blob_config", default=__get_fullpath('./mobilenet-ssd/mobilenet-ssd.json'), type=str, help="Path to nnet model config .json file")
    parser.add_argument('-p', '--path', default="data", type=str, help="Path where to store the captured data")

    parser.add_argument(
        "-s", "--streams",
        nargs="+",
        type=_stream_type,
        dest="streams",
        default=["metaout", "previewout"],
        help="Define which streams to enable \n"
             "Format: stream_name or stream_name,max_fps \n"
             "Example: -s metaout previewout \n"
             "Example: -s metaout previewout,10 depth_sipp,10"
    )
    args = parser.parse_args()

    dest = Path(args.path).resolve().absolute()

    if dest.exists() and len(list(dest.glob('*'))) != 0:
        raise ValueError(
            f"Path {dest} contains {len(list(dest.glob('*')))} files. Either specify new path or remove files from this directory")
    dest.mkdir(parents=True, exist_ok=True)

    if args.nodisplay and args.time < 1:
        raise ValueError("You need to provide a correct time limit for the recording if used without display")

    device = depthai.Device("", False)

    p = device.create_pipeline(config={
        "streams": args.streams,
        "ai": {
            "blob_file": args.blob,
            "blob_file_config": args.blob_config
        },
        'camera': {
            'mono': {
                'resolution_h': 720, 'fps': 30
            },
        },
    })

    if p is None:
        raise RuntimeError("Error initializing pipelne")

    start_ts = time.time()
    nnet_storage = []
    frames_storage = []

    with open(args.blob_config) as f:
        blob_config = json.load(f)
        key_mappings = blob_config['tensors'][0]['property_key_mapping']
        field_names = []
        for arr in key_mappings:
            if len(arr) > 0:
                field_names = arr
                break

    with ThreadPoolExecutor(max_workers=100) as pool:
        while args.time < 0 or time.time() - start_ts < args.time:
            if args.ai:
                nnet_packets, data_packets = p.get_available_nnet_and_data_packets()

                for nnet_packet in nnet_packets:
                    for e in nnet_packet.entries():
                        if e[0]['id'] == -1.0 or e[0]['confidence'] == 0.0:
                            break
                        entry = {}
                        for field in field_names:
                            entry[field] = e[0][field]
                        nnet_storage.append((time.time(), "nnet", entry))
            else:
                data_packets = p.get_available_data_packets()

            for packet in data_packets:
                frame = packet.getData()

                if packet.stream_name in ('disparity_color', "depth_raw") and len(frame.shape) == 2 and frame.dtype != np.uint8:
                    frame = (65535 // frame).astype(np.uint8)
                    frame = cv2.applyColorMap(frame, cv2.COLORMAP_HOT)

                if frame is not None:
                    frames_storage.append((time.time(), packet.stream_name, frame))

                    if packet.stream_name == 'previewout':
                        data = packet.getData()
                        data0 = data[0, :, :]
                        data1 = data[1, :, :]
                        data2 = data[2, :, :]
                        frame = cv2.merge([data0, data1, data2])
                    cv2.imshow(packet.stream_name, frame)

            if cv2.waitKey(1) == ord('q'):
                break

        with open(dest / Path('dataset.tsv'), 'w') as out_file:
            for ts, source, data in sorted([*frames_storage, *nnet_storage], key=lambda item: item[0]):
                filename = Path(f"{int((ts - start_ts) * 10000)}-{source}")
                if source == "nnet":
                    filename = filename.with_suffix('.json')
                    with open(dest / filename, 'w') as f:
                        json.dump(data, f)
                else:
                    filename = filename.with_suffix('.npy')
                    pool.submit(np.save, dest / filename, data)
                tsv_writer = csv.writer(out_file, delimiter='\t')
                tsv_writer.writerow([ts - start_ts, source, filename])


if __name__ == "__main__":
    record_depthai_mockups()