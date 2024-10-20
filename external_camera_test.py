import cv2
import os
from subprocess import PIPE, run

def get_camera_index():
    usb_needle = "USB Camera"
    buildin_needle = "FaceTime HD Camera (Built-in)"
    command = ['ffmpeg','-f', 'avfoundation','-list_devices','true','-i','""']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    usb_id = None
    builtin_id = None
    for item in result.stderr.splitlines():
        print(item)
        if usb_needle in item:
            usb_id = int(item.split("[")[2].split(']')[0])
        if buildin_needle in item:
            builtin_id = int(item.split("[")[2].split(']')[0])

    if usb_id is not None:
        return usb_id
    return builtin_id


cam_id = get_camera_index()
cap = cv2.VideoCapture(cam_id)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
ret_val , cap_for_exposure = cap.read()