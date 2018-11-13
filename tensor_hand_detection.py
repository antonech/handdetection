import cv2
import threading
import signal
import tensorflow as tf
import numpy as np
from queue import Queue

img_queue = Queue()
output_q = Queue()


class TensorflowDetector(object):

    MODEL_NAME = ''
    PATH_TO_LABELS = ''
    PATH_TO_MODEL = 'frozen_inference_graph.pb'
    __lock = threading.RLock()

    def __init__(self, **kwargs):
        self.img_queue = kwargs.pop('img_queue', img_queue)
        self.output_q = kwargs.pop('output_q', output_q)

        self.graph_path = kwargs.pop('graph_path', self.PATH_TO_MODEL)
        self.src = kwargs.pop('src', 0)
        self.width = kwargs.pop('width', 1280)
        self.height = kwargs.pop('height', 720)
        self.score_thresh = kwargs.pop('score_thresh', 0.9)
        self.standalone = kwargs.get('standalone', True)

        self.detection_graph = tf.Graph()

        self.threads = []

        self.started = False

        th1 = threading.Thread(name='worker', target=self.worker)
        self.threads.append(th1)

        th2 = threading.Thread(name='stream_reader', target=self.stream_reader)
        self.threads.append(th2)

        if self.standalone:
            th3 = threading.Thread(name='img_show', target=self.plot)
            self.threads.append(th3)

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

        return np.squeeze(boxes), np.squeeze(scores), np.squeeze(classes)

    def load_label_map(self):
        pass

    def stream_reader(self):

        while self.started:
            grabbed, frame = self.stream.read()

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if self.img_queue.qsize() <= 1:
                self.img_queue.put(frame)

    def draw_box(self, img, boxes, scores, classes):
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

        while self.started:
            if self.output_q.qsize():
                img = self.output_q.get()[0]
            else:
                continue

            frame = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            frame = cv2.flip(frame, 1)

            cv2.imshow('Stream', frame)
            self.output_q.task_done()

            cv2.waitKey(1)

    def worker(self):
        while self.started:
            if self.img_queue.qsize():
                img = self.img_queue.get()
                boxes, scores, classes = self.get_classification(img)
                if self.standalone:
                    img = self.draw_box(img,  boxes, scores, classes)
                self.output_q.put((img, boxes, scores, classes))

        self.sess.close()

    def start(self):

        if self.started:
            return

        self.started = True

        for th in self.threads:
            th.daemon = True
            th.start()

        if self.standalone:
            try:
                signal.pause()
            except KeyboardInterrupt:
                self.stop()

    def join(self):
        for th in self.threads:
            th.join()

    def stop(self):
        self.started = False
        self.join()


if __name__ == '__main__':
    tfd = TensorflowDetector(score_thresh=0.9)
    tfd.start()
    tfd.join()
