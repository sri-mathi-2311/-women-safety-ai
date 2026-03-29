
import requests
import cv2
import numpy as np

try:
    r = requests.get('http://127.0.0.1:8000/api/video/feed', stream=True, timeout=5)
    bytes_data = bytes()
    for chunk in r.iter_content(chunk_size=1024):
        bytes_data += chunk
        a = bytes_data.find(b'\xff\xd8')
        b = bytes_data.find(b'\xff\xd9')
        if a != -1 and b != -1:
            jpg = bytes_data[a:b+2]
            bytes_data = bytes_data[b+2:]
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            if img is not None:
                print(f'Frame received, shape: {img.shape}, average pixel: {img.mean()}')
                cv2.imwrite('test_frame.jpg', img)
                break
except Exception as e:
    print('Error:', e)

