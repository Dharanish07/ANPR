import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import easyocr
import util

model_cfg_path = "C:/Users/cjdha/Downloads/automatic-number-plate-recognition-python-master (1)/automatic-number-plate-recognition-python-master/yolov3-from-opencv-object-detection/model/cfg/darknet-yolov3.cfg"
model_weights_path = "C:/Users/cjdha/Downloads/automatic-number-plate-recognition-python-master (1)/automatic-number-plate-recognition-python-master/yolov3-from-opencv-object-detection/model/weights/model.weights"
class_names_path = "C:/Users/cjdha/Downloads/automatic-number-plate-recognition-python-master (1)/automatic-number-plate-recognition-python-master/yolov3-from-opencv-object-detection/model/class.names"

input_dir = "C:/Users/cjdha/Downloads/automatic-number-plate-recognition-python-master (1)/automatic-number-plate-recognition-python-master/image"

for img_name in os.listdir(input_dir):
    img_path = os.path.join(input_dir, img_name)
    with open(class_names_path, 'r') as f:
        class_names = [j[:-1] for j in f.readlines() if len(j) > 2]
        f.close()
    net = cv2.dnn.readNetFromDarknet(model_cfg_path, model_weights_path)
    img = cv2.imread(img_path)
    H, W, _ = img.shape
    blob = cv2.dnn.blobFromImage(img, 1 / 255, (416, 416), (0, 0, 0), True)
    net.setInput(blob)
    detections = util.get_outputs(net)
    bboxes = []
    class_ids = []
    scores = []

    for detection in detections:
        bbox = detection[:4]
        xc, yc, w, h = bbox
        bbox = [int(xc * W), int(yc * H), int(w * W), int(h * H)]
        bbox_confidence = detection[4]
        class_id = np.argmax(detection[5:])
        score = np.amax(detection[5:])
        bboxes.append(bbox)
        class_ids.append(class_id)
        scores.append(score)

    bboxes, class_ids, scores = util.NMS(bboxes, class_ids, scores)
    reader = easyocr.Reader(['en'])
    
    for bbox_, bbox in enumerate(bboxes):
        xc, yc, w, h = bbox
        license_plate = img[int(yc - (h / 2)):int(yc + (h / 2)), int(xc - (w / 2)):int(xc + (w / 2)), :].copy()
        img = cv2.rectangle(img,
                            (int(xc - (w / 2)), int(yc - (h / 2))),
                            (int(xc + (w / 2)), int(yc + (h / 2))),
                            (0, 255, 0),
                            15)

        license_plate_gray = cv2.cvtColor(license_plate, cv2.COLOR_BGR2GRAY)
        _, license_plate_thresh = cv2.threshold(license_plate_gray, 64, 255, cv2.THRESH_BINARY_INV)
        output = reader.readtext(license_plate_thresh)
        for out in output:
            text_bbox, text, text_score = out
            if text_score > 0.4:
                print(text, text_score)

    plt.figure()
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    plt.figure()
    plt.imshow(cv2.cvtColor(license_plate, cv2.COLOR_BGR2RGB))

    plt.figure()
    plt.imshow(cv2.cvtColor(license_plate_gray, cv2.COLOR_BGR2RGB))

    plt.figure()
    plt.imshow(cv2.cvtColor(license_plate_thresh, cv2.COLOR_BGR2RGB))

    plt.show()
