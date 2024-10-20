# import cv2
# import numpy as np
# # img = cv2.imread('Ping-pong-OpenCV-master/starfield.png')
# # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# # print("img size is {}".format(img.shape))
# height = 600
# width = 800
# img = np.ones((height, width, 3), dtype=np.uint8) * 255


# cv2.line(img, (10, 10), (400, 100), (0, 0, 125), 2)
# cv2.namedWindow('image', cv2.WINDOW_NORMAL)
# cv2.resizeWindow('image', 700, 500)
# cv2.imshow("image", img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

import cv2

def find_external_camera(max_index=5):
    external_camera_index = None

    for index in range(max_index):
        try:
            cap = cv2.VideoCapture(index)

            # Check if the camera is opened correctly
            if not cap.isOpened():
                print(f"Camera at index {index} could not be opened.")
                continue

            # Capture a frame to get camera properties
            ret, frame = cap.read()
            if not ret:
                print(f"Failed to read from camera {index}.")
                cap.release()
                continue

            # Check resolution or any other property to identify the external camera
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print(f"Camera {index} resolution: {width}x{height}")

            # Assume your external camera has a specific resolution (example: >= 1280x720)
            # if width >= 1279 and height <= 721:
            #     external_camera_index = index
            #     cap.release()
            #     break  # Exit the loop when the external camera is found

            cap.release()

        except Exception as e:
            print(f"Error with camera {index}: {e}")

    return external_camera_index

# Call the function to find the external camera
external_camera_index = find_external_camera(max_index=2)  # Adjust max_index as needed
if external_camera_index is not None:
    print(f"External camera found at index {external_camera_index}")
else:
    print("No external camera found.")
