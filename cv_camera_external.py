import cv2

import os
from subprocess import PIPE, run

def find_external_camera(max_index=5):
    external_camera_index = None

    for index in range(max_index):
        cap = cv2.VideoCapture(index)

        # Check if the camera is opened correctly
        if not cap.isOpened():
            print(f"Camera at index {index} could not be opened.")
            continue

        # Check camera properties (e.g., resolution)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"Camera {index} resolution: {width}x{height}")

        # Assuming external camera has a specific resolution (example: >= 1280x720)
        if width >= 1280 and height == 720:
            external_camera_index = index
            cap.release()  # Release the camera after detecting it
            break  # Exit the loop once the external camera is found

        cap.release()  # Ensure the camera is released after each check

    return external_camera_index

# Find the external camera
# external_camera_index = find_external_camera(max_index=10)

def get_camera_index():
    usb_needle = "USB Camera"
    buildin_needle = "FaceTime HD Camera (Built-in)"
    command = ['ffmpeg','-f', 'avfoundation','-list_devices','true','-i','""']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    usb_id = None
    builtin_id = None
    for item in result.stderr.splitlines():
        # print(item)
        if usb_needle in item:
            usb_id = int(item.split("[")[2].split(']')[0])
        if buildin_needle in item:
            builtin_id = int(item.split("[")[2].split(']')[0])

    if usb_id is not None:
        return usb_id
    return builtin_id


external_camera_index = get_camera_index()

if external_camera_index is not None:
    print(f"External camera found at index {external_camera_index}")

    # Re-open the camera after finding the correct index
    cap = cv2.VideoCapture(external_camera_index)
    
    if not cap.isOpened():
        print(f"Error: Camera {external_camera_index} could not be opened.")
        exit()

    # Main loop to capture video
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to grab frame")
            break
        
        cv2.imshow('External Camera Feed', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

else:
    print("No external camera found.")


print(cv2.__version__)
