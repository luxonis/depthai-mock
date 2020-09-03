import cv2

from pipeline import MockupCNNPipeline

p = MockupCNNPipeline(data_path="data")

while True:
    data_packets = p.get_available_data_packets()
    for packet in data_packets:
        if packet.stream_name == 'previewout':
            data = packet.getData()
            data0 = data[0, :, :]
            data1 = data[1, :, :]
            data2 = data[2, :, :]
            frame = cv2.merge([data0, data1, data2])

            cv2.imshow('previewout', frame)

    if cv2.waitKey(1) == ord('q'):
        break
