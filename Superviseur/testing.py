### version ou la detection sera fait dans la fonction get_frame

import logging
import threading
import cv2
from django.http import HttpResponseBadRequest, HttpResponseServerError, StreamingHttpResponse
from ultralytics import YOLO


class VideoCamera(object):
    def _init_(self, rtsp_url, model):
        self.video = cv2.VideoCapture(rtsp_url)
        self.model = model
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def _del_(self):
        self.video.release()

    def get_frame(self):
        if not self.grabbed or self.frame is None:
            return None  # Return None if the frame is empty
        
        # Object detection using YOLO model
        results = self.model.predict(self.frame,)
        res_plotted = results[0].plot()
        _, jpeg = cv2.imencode('.jpg', res_plotted)
        
        return jpeg.tobytes()

    def update(self):
        try:
            while True:
                (self.grabbed, self.frame) = self.video.read()
        except Exception as e:
            self.video.release()

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame is None:
            continue  # Skip yielding None frames
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

logger = logging.getLogger(__name__)

@login_required # type: ignore
def livefe(request):

    rtsp_url = request.GET.get('rtsp', "")
    
    if not rtsp_url:
        return HttpResponseBadRequest("No RTSP URL provided.")
    
    # Load YOLO model
    model = YOLO('yolov8s.pt')
    
    try:
        return StreamingHttpResponse(gen(VideoCamera(rtsp_url, model)), content_type='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        logger.exception("Error in livefe view")
        return HttpResponseServerError("Failed to start the live feed.")









### version ou le detection sera fait dans la fonction update    
    
    
# class VideoCamera(object):
#     def _init_(self, rtsp_url, model):
#         self.video = cv2.VideoCapture(rtsp_url)
#         self.model = model
#         (self.grabbed, self.frame) = self.video.read()
#         threading.Thread(target=self.update, args=()).start()

#     def _del_(self):
#         self.video.release()

#     def get_frame(self):
#         if not self.grabbed or self.frame is None:
#             return None  # Return None if the frame is empty
        
#         # Directly return the frame without object detection
#         _, jpeg = cv2.imencode('.jpg', self.frame)
#         return jpeg.tobytes()

#     def update(self):
#         try:
#             while True:
#                 (self.grabbed, frame) = self.video.read()
#                 if self.grabbed:
#                     # Perform object detection using YOLO model
#                     results = self.model.predict(self.frame)
#                     res_plotted = results[0].plot()
#                     self.frame = res_plotted
#         except Exception as e:
#             self.video.release()

# def gen(camera):
#     while True:
#         frame = camera.get_frame()
#         if frame is None:
#             continue  # Skip yielding None frames
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# logger = logging.getLogger(_name_)

# @login_required
# def livefe(request):
#     rtsp_url = request.GET.get('rtsp', "")
#     if not rtsp_url:
#         return HttpResponseBadRequest("No RTSP URL provided.")
    
#     # Load YOLO model
#     model = YOLO('yolov8s.pt')
    
#     try:
#         return StreamingHttpResponse(gen(VideoCamera(rtsp_url, model)), content_type='multipart/x-mixed-replace; boundary=frame')
#     except Exception as e:
#         logger.exception("Error in livefe view")
#         return HttpResponseServerError("Failed to start the live feed.")