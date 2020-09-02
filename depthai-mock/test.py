import cv2

from pipeline import MockupCNNPipeline

p = MockupCNNPipeline(data_path="data")
p.get_available_data_packets()

while True:
    data_packets = p.get_available_data_packets()

    for frame in data_packets:
        cv2.imshow('previewout', frame)

    if cv2.waitKey(1) == ord('q'):
        break
