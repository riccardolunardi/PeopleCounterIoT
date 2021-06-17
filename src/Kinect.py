import cv2
import dlib
import freenect
import imutils
import numpy as np
import imutils.video

from tracking_src import config, thread, frame_convert2
from bases.Contapersone import Contapersone
from tracking_src.centroidtracker import CentroidTracker
from tracking_src.trackableobject import TrackableObject


class Kinect(Contapersone):
    def __init__(self, id_contapersone=1, config_file="../config/simulatore.json", debug=0):
        super().__init__(id_contapersone, config_file)

    @staticmethod
    def get_depth():
        return freenect.sync_get_depth()[0]
        # return mylib.frame_convert2.pretty_depth_cv(freenect.sync_get_depth()[0])

    def main_procedure(self):
        skip_frames = 10

        # initialize the frame dimensions (we'll set them as soon as we read
        # the first frame from the video)
        w = None
        h = None

        # instantiate our centroid tracker, then initialize a list to store
        # each of our dlib correlation trackers, followed by a dictionary to
        # map each unique object ID to a TrackableObject
        ct = CentroidTracker(maxDisappeared=25, maxDistance=60)
        trackers = []
        trackable_objects = {}

        # initialize the total number of frames processed thus far, along
        # with the total number of objects that have moved either up or down
        total_frames = 0
        total_down = 0
        total_up = 0
        x = []
        empty = []
        empty1 = []

        fps = imutils.video.FPS().start()

        min_countour_area = 4000
        max_countour_area = 40000

        back_sub = cv2.createBackgroundSubtractorKNN(history=70, dist2Threshold=200, detectShadows=False)

        vs = thread.ThreadingClass()

        # loop over frames from the video stream
        while True:
            # grab the next frame and handle if we are reading from either
            # VideoCapture or VideoStream
            frame = vs.read()
            # frame = frame[1] if args.get("input", False) else frame

            # if we are viewing a video and we did not grab a frame then we
            # have reached the end of the video
            if frame is None:
                break

            # resize the frame to have a maximum width of 500 pixels (the
            # less data we have, the faster we can process it), then convert
            # the frame from BGR to RGB for dlib

            frame = imutils.resize(frame, width=300)
            # frame = cv2.rotate(frame, cv2.cv2.ROTATE_90_CLOCKWISE)
            # frame = frame[0:260, 0:500]
            # drawing_frame = tracking_src.frame_convert2.pretty_depth(frame)
            # drawing_frame = frame

            current_depth = 715
            threshold = 200
            frame = 255 * np.logical_and(frame >= current_depth - threshold,
                                         frame <= current_depth + threshold)

            frame = frame.astype(np.uint8)
            frame = back_sub.apply(frame)
            # cv2.imshow("Real-Time Monitoring/Analysis Window3", frame)

            # rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            drawing_frame = frame_convert2.pretty_depth(frame)
            frame = cv2.medianBlur(frame, 11)

            # if the frame dimensions are empty, set them
            if w is None or h is None:
                (h, w) = frame.shape[:2]

            # initialize the current status along with our list of bounding
            # box rectangles returned by either (1) our object detector or
            # (2) the correlation trackers
            status = "Waiting"
            rects = []

            # check to see if we should run a more computationally expensive
            # object detection method to aid our tracker
            if total_frames % skip_frames == 0:
                # set the status and initialize our new set of object trackers
                status = "Detecting"
                trackers = []

                # convert the frame to a blob and pass the blob through the
                # network and obtain the detections
                # gray-scale convertion and Gaussian blur filter applying

                # Applicazione in range
                kernel = np.ones((10, 10), np.uint8)

                # frame = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)
                frame = cv2.morphologyEx(frame, cv2.MORPH_CLOSE, kernel)

                cnts = cv2.findContours(frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)

                # loop over the detections
                for c in cnts:
                    # compute the (x, y)-coordinates of the bounding box
                    # for the object
                    # if a contour has small area, it'll be ignored
                    if cv2.contourArea(c) < min_countour_area or cv2.contourArea(c) > max_countour_area:
                        continue

                    print(cv2.contourArea(c))
                    # draw an rectangle "around" the object
                    (start_x, start_y, end_x, end_y) = cv2.boundingRect(c)
                    cv2.rectangle(
                        drawing_frame,
                        (start_x, start_y),
                        (start_x + end_x, start_y + end_y),
                        (255, 255, 255),
                        2
                    )

                    # construct a dlib rectangle object from the bounding
                    # box coordinates and then start the dlib correlation
                    # tracker
                    tracker = dlib.correlation_tracker()
                    rect = dlib.rectangle(start_x, start_y, start_x + end_x, start_y + end_y)
                    tracker.start_track(frame, rect)

                    # add the tracker to our list of trackers so we can
                    # utilize it during skip frames
                    trackers.append(tracker)

            # otherwise, we should utilize our object *trackers* rather than
            # object *detectors* to obtain a higher frame processing throughput
            else:
                # loop over the trackers
                for tracker in trackers:
                    # set the status of our system to be 'tracking' rather
                    # than 'waiting' or 'detecting'
                    status = "Tracking"

                    # update the tracker and grab the updated position
                    tracker.update(frame)
                    pos = tracker.get_position()

                    # unpack the position object
                    start_x = int(pos.left())
                    start_y = int(pos.top())
                    end_x = int(pos.right())
                    end_y = int(pos.bottom())

                    # add the bounding box coordinates to the rectangles list
                    rects.append((start_x, start_y, end_x, end_y))

            # draw a horizontal line in the center of the frame -- once an
            # object crosses this line we will determine whether they were
            # moving 'up' or 'down'
            # cv2.line(frame, (0, 3*H // 5), (W, 3*H // 5), (255, 255, 255), 3)
            cv2.line(drawing_frame, (0, h // 2), (w, h // 2), (255, 255, 255), 3)
            # cv2.putText(
            #     drawing_frame,
            #     "-Prediction border - Entrance-",
            #     (10, h - ((len(cnts) * 20) + 200)),
            #     cv2.FONT_HERSHEY_SIMPLEX,
            #     0.5,
            #     (255, 255, 255),
            #     1
            # )

            # use the centroid tracker to associate the (1) old object
            # centroids with (2) the newly computed object centroids
            objects = ct.update(rects)

            # loop over the tracked objects
            for (objectID, centroid) in objects.items():
                # check to see if a trackable object exists for the current
                # object ID
                to = trackable_objects.get(objectID, None)

                # if there is no existing trackable object, create one
                if to is None:
                    to = TrackableObject(objectID, centroid)

                # otherwise, there is a trackable object so we can utilize it
                # to determine direction
                else:
                    # the difference between the y-coordinate of the *current*
                    # centroid and the mean of *previous* centroids will tell
                    # us in which direction the object is moving (negative for
                    # 'up' and positive for 'down')
                    y = [c[1] for c in to.centroids]
                    direction = centroid[1] - np.mean(y)
                    to.centroids.append(centroid)

                    # check to see if the object has been counted or not
                    if not to.counted:
                        # if the direction is negative (indicating the object
                        # is moving up) AND the centroid is above the center
                        # line, count the object
                        if direction < 0 and centroid[1] < h // 2:
                            total_up += 1
                            empty.append(total_up)
                            to.counted = True
                            self.send(self.gen_passaggio_object(1))

                        # if the direction is positive (indicating the object
                        # is moving down) AND the centroid is below the
                        # center line, count the object
                        elif direction > 0 and centroid[1] > h // 2:
                            total_down += 1
                            empty1.append(total_down)
                            x = [len(empty1) - len(empty)]
                            to.counted = True
                            self.send(self.gen_passaggio_object(-1))

                # store the trackable object in our dictionary
                trackable_objects[objectID] = to

                # draw both the ID of the object and the centroid of the
                # object on the output frame
                text = "ID {}".format(objectID)
                cv2.putText(drawing_frame, text, (centroid[0] - 10, centroid[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                cv2.circle(drawing_frame, (centroid[0], centroid[1]), 4, (255, 255, 255), -1)

            # construct a tuple of information we will be displaying on the
            info = [
                ("Exit", total_up),
                ("Enter", total_down),
                ("Status", status),
            ]

            info2 = [("Total people inside", x), ]

            # Display the output
            for (i, (k, v)) in enumerate(info):
                text = "{}: {}".format(k, v)
                cv2.putText(drawing_frame, text, (10, h - ((i * 20) + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                            (255, 255, 255), 2)

            for (i, (k, v)) in enumerate(info2):
                text = "{}: {}".format(k, v)
                cv2.putText(drawing_frame, text, (265, h - ((i * 20) + 60)), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                            (255, 255, 255), 2)

            # show the output frame
            cv2.imshow("Real-Time Monitoring/Analysis Window", drawing_frame)
            key = cv2.waitKey(1) & 0xFF

            # increment the total number of frames processed thus far and
            # then update the FPS counter
            total_frames += 1
            fps.update()

            # if the 'q' key was pressed, break from the loop
            if key == ord("q"):
                break

        # stop the timer and display FPS information
        fps.stop()
        print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

        # close any open windows
        cv2.destroyAllWindows()


if __name__ == "__main__":
    device = Kinect(id_contapersone=2)
    device.main_procedure()
