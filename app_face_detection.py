import cv2
import numpy as np
import streamlit as st
from PIL import Image
import joblib  # Thư viện để tải mô hình đã lưu

def run_app3():
    st.title("Ứng dụng phát hiện khuôn mặt")

    # Tải lên ảnh
    uploaded_image = st.file_uploader("Tải lên một ảnh", type=["jpg", "jpeg", "png"])

    if uploaded_image is not None:
        # Đọc ảnh tải lên
        image = Image.open(uploaded_image)
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)  # Chuyển đổi sang ảnh xám

        # Hiển thị ảnh đã tải lên
        st.image(image, caption="Ảnh đã tải lên", use_column_width=True)

        # Gọi hàm phát hiện khuôn mặt
        boxes = sliding_window_detect(image, knn_model)

        # Chọn box tốt nhất
        selected_boxes = non_max_suppression(boxes, overlap_threshold=0.3)

        # Vẽ các box lên ảnh
        result_img = draw_boxes(image, selected_boxes)

        # Hiển thị kết quả
        st.image(result_img, caption="Kết quả phát hiện khuôn mặt", use_column_width=True)

def sliding_window_detect(img, model, step_size=5, window_size=(100, 100)):
    boxes = []
    height, width = img.shape

    window_width = window_size[0]
    window_height = window_size[1]

    for y in range(0, height - window_height + 1, step_size):
        for x in range(0, width - window_width + 1, step_size):
            window = img[y:y + window_height, x:x + window_width]
            if window.shape[0] != window_height or window.shape[1] != window_width:
                continue

            pred = detect_face(window, model)
            if pred == 1:
                boxes.append((x, y, window_width, window_height))

    return boxes

def detect_face(img, model):
    img_resized = cv2.resize(img, (24, 24)).flatten()
    pred = model.predict([img_resized])
    return pred[0]

def draw_boxes(img, boxes):
    for (x, y, w, h) in boxes:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return img

def non_max_suppression(boxes, overlap_threshold=0.3):
    if len(boxes) == 0:
        return []

    boxes = np.array(boxes)
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 0] + boxes[:, 2]
    y2 = boxes[:, 1] + boxes[:, 3]

    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    order = np.argsort(y2)

    picked_boxes = []

    while len(order) > 0:
        i = order[-1]
        picked_boxes.append(boxes[i])

        xx1 = np.maximum(x1[i], x1[order[:-1]])
        yy1 = np.maximum(y1[i], y1[order[:-1]])
        xx2 = np.minimum(x2[i], x2[order[:-1]])
        yy2 = np.minimum(y2[i], y2[order[:-1]])

        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        overlap = (w * h) / areas[order[:-1]]

        order = order[np.where(overlap <= overlap_threshold)[0]]

    return picked_boxes

if __name__ == "__main__":
    knn_model_path = '/content/drive/MyDrive/Mydrive/Githut/faces_and_non_faces_data/knn_model.pkl'
    knn_model = joblib.load(knn_model_path)
    run_app3()
