import sys
import cv2
import threading

import tensorflow as tf
import numpy as np
from time import sleep
from queue import Queue


class TensorflowDetector(object):

    MODEL_NAME = ''
    PATH_TO_LABELS = ''
    PATH_TO_MODEL = 'frozen_inference_graph.pb'

    def __init__(self, **kwargs):
        self.graph_path = kwargs.pop('graph_path', self.PATH_TO_MODEL)
        self.src = kwargs.pop('src', 0)
        self.width = kwargs.pop('width', 1280)
        self.height = kwargs.pop('height', 720)
        self.score_thresh = kwargs.pop('score_thresh', 0.8)

        self.detection_graph = tf.Graph()
        self.img_queue = Queue()
        self.output_q = Queue()

        self.stopped = True
        self.started = False

        self.stream = cv2.VideoCapture(self.src)
        codec = 1196444237.0  # MJPG

        self.stream.set(cv2.CAP_PROP_FOURCC, codec)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            # Works up to here.
            with tf.gfile.GFile(self.graph_path, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
            self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
            self.d_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
            self.d_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
            self.d_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
            self.num_d = self.detection_graph.get_tensor_by_name('num_detections:0')
            self.sess = tf.Session(graph=self.detection_graph)

    def get_classification(self, img):
        # Bounding Box Detection.
        # Expand dimension since the model expects image to have shape [1, None, None, 3].
        img_expanded = np.expand_dims(img, axis=0)

        boxes, scores, classes, num = self.sess.run(
            [self.d_boxes, self.d_scores, self.d_classes, self.num_d],
            feed_dict={self.image_tensor: img_expanded})

        return np.squeeze(boxes), np.squeeze(scores), np.squeeze(classes), np.squeeze(num)

    def load_label_map(self):
        pass

    def stream_reader(self):
        while not self.stopped:
            # otherwise, read the next frame from the stream

            grabbed, frame = self.stream.read()

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            self.img_queue.put(frame)

            sleep(0.1)

    def draw_box(self, img, boxes, scores, classes, num):
        height = img.shape[0]
        width = img.shape[1]
        for i, score in enumerate(scores):
            if score > self.score_thresh:
                print(score, classes[i])
                (left, right, top, bottom) = (boxes[i][1] * width, boxes[i][3] * width,
                                              boxes[i][0] * height, boxes[i][2] * height)
                p1 = (int(left), int(top))
                p2 = (int(right), int(bottom))
                cv2.rectangle(img, p1, p2, (77, 255, 9), 3, 1)
                return img

        return img

    def plot(self):
        cv2.startWindowThread()
        cv2.namedWindow('Stream')

        while not self.stopped:
            img = self.output_q.get()

            frame = cv2.cvtColor(img[0], cv2.COLOR_RGB2BGR)
            frame = cv2.flip(frame, 1)

            cv2.imshow('Stream', frame)
            cv2.waitKey(1)

    def worker(self):
        while not self.stopped:
            if not self.img_queue.empty():
                img = self.img_queue.get()
                boxes, scores, classes, num = self.get_classification(img)
                img = self.draw_box(img,  boxes, scores, classes, num)
                self.output_q.put((img, boxes, scores))

        self.sess.close()

    def start(self):

        if not self.started:
            self.stopped = False
            th1 = threading.Thread(name='worker', target=self.worker)
            count = 5
            while count > 0:
                sleep(1)
                print('.', end='')
                sys.stdout.flush()
                count -= 1

            th2 = threading.Thread(name='stream_reader', target=self.stream_reader)
            th3 = threading.Thread(name='img_show', target=self.plot)

            th1.daemon = True
            th1.start()
            th2.daemon = True
            th2.start()

            th3.daemon = True
            th3.start()

            self.started = True

            try:
                th1.join()
                th2.join()
                th3.join()
            except KeyboardInterrupt:
                self.stop()

    def stop(self):
        self.stopped = True
        self.started = False


if __name__ == '__main__':
    tfd = TensorflowDetector(score_thresh=0.9)
    tfd.start()
