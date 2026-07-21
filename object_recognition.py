import os
import cv2
import numpy as np

# أسماء الفئات التي يستطيع نموذج MobileNet SSD التعرف عليها
CLASSES = [
    "background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair",
    "cow", "diningtable", "dog", "horse", "motorbike",
    "person", "pottedplant", "sheep", "sofa", "train",
    "tvmonitor"
]

# مسارات ملفات النموذج
PROTOTXT_PATH = "model/deploy.prototxt"
MODEL_PATH = "model/mobilenet_iter_73000.caffemodel"

# مجلدات الصور والنتائج
IMAGES_FOLDER = "images"
RESULTS_FOLDER = "results"

# أقل نسبة ثقة نقبلها,a fu]
CONFIDENCE_THRESHOLD = 0.40

# التحقق من وجود ملفات النموذج
if not os.path.exists(PROTOTXT_PATH):
    raise FileNotFoundError(f"Model file not found: {PROTOTXT_PATH}")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

# إنشاء مجلد النتائج إذا لم يكن موجودًا
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# تحميل النموذج
net = cv2.dnn.readNetFromCaffe(PROTOTXT_PATH, MODEL_PATH)
# امتدادات الصور المدعومة
supported_extensions = (".jpg", ".jpeg", ".png")

image_files = [
    file_name
    for file_name in os.listdir(IMAGES_FOLDER)
    if file_name.lower().endswith(supported_extensions)
]

if not image_files:
    raise FileNotFoundError(
        "No images were found inside the images folder."
    )

for image_name in image_files:
    image_path = os.path.join(IMAGES_FOLDER, image_name)
    image = cv2.imread(image_path)

    if image is None:
        print(f"Could not read image: {image_name}")
        continue

    height, width = image.shape[:2]

    # تجهيز الصورة للنموذج
    blob = cv2.dnn.blobFromImage(
        cv2.resize(image, (300, 300)),
        scalefactor=0.007843,
        size=(300, 300),
        mean=127.5
    )

    net.setInput(blob)
    detections = net.forward()

    detected_objects = 0

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence >= CONFIDENCE_THRESHOLD:
            class_id = int(detections[0, 0, i, 1])

            if class_id >= len(CLASSES):
                continue

            box = detections[0, 0, i, 3:7] * np.array(
                [width, height, width, height]
            )

            start_x, start_y, end_x, end_y = box.astype("int")

            # منع الإحداثيات من الخروج عن حدود الصورة
            start_x = max(0, start_x)
            start_y = max(0, start_y)
            end_x = min(width - 1, end_x)
            end_y = min(height - 1, end_y)

            label = f"{CLASSES[class_id]}: {confidence * 100:.1f}%"

            cv2.rectangle(
                image,
                (start_x, start_y),
                (end_x, end_y),
                (0, 255, 0),
                2
            )

            text_y = start_y - 10 if start_y > 20 else start_y + 20

            cv2.putText(
                image,
                label,
                (start_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            detected_objects += 1

    result_name = f"detected_{image_name}"
    result_path = os.path.join(RESULTS_FOLDER, result_name)

    cv2.imwrite(result_path, image)

    print(
        f"{image_name}: {detected_objects} object(s) detected "
        f"and saved to {result_path}"
    )

print("Object recognition completed successfully.")
