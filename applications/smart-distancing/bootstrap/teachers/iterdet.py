import copy
import os
import time
import logging
import wget
from mmdet.apis import init_detector, inference_detector
import cv2 as cv
from teacher_meta_arch import TeacherMetaArch
import torch


class IterDet(TeacherMetaArch):
    """ IterDet object detection model"""

    def __init__(self, config):
        """
        IterDet class constructor
        Args:
            config: a bootstrap config file
        """
        super(IterDet, self).__init__(config=config)
        self.detection_model = self.load_model()
        self.postprocessing_method = self.config.get_section_dict('Teacher')['PostProcessing']
        # weather or not using background filtering in postprocessing step
        self.background_filter = True if self.postprocessing_method == "background_filter" else False
        if self.background_filter:
            self.background_subtractor = cv.createBackgroundSubtractorMOG2()

    def inference(self, preprocessed_image):
        """
        predict bounding boxes of a preprocessed image
        Args:
            preprocessed_image: a preprocessed RGB frame

        Returns:
            A list of dictionaries, each item has the id, relative bounding box coordinate and prediction confidence score
             of one detected instance.
        """
        self.frame = preprocessed_image
        output_dict = inference_detector(self.detection_model, preprocessed_image)
        class_id = int(self.config.get_section_dict('Teacher')['ClassID'])
        score_threshold = float(self.config.get_section_dict('Teacher')['MinScore'])
        result = []
        for i, box in enumerate(output_dict[0]):  # number of boxes
            if box[-1] > score_threshold:
                result.append({"id": str(class_id) + '-' + str(i),
                               "bbox": [box[0] / self.image_size[0], box[1] / self.image_size[1],
                                        box[2] / self.image_size[0], box[3] / self.image_size[1]],
                               "score": box[-1]})

        return result

    def postprocessing(self, raw_results):
        """
        omit large boxes and boxes that detected as background by background subtractor.
        Args:
            raw_results: list of dictionaries, output of the inference method
        Returns:
            a filter version of raw_results
        """
        post_processed_results = copy.copy(raw_results)
        for bbox in raw_results:
            # delete large boxes
            if (bbox["bbox"][2] - bbox["bbox"][0]) * (bbox["bbox"][3] - bbox["bbox"][1]) > 0.2:
                post_processed_results.remove(bbox)
                continue
            # delete background boxes
            if self.background_filter:
                foreground_mask = self.background_subtractor.apply(self.frame)
                foreground_mask = cv.threshold(foreground_mask, 128, 255, cv.THRESH_BINARY)[1] / 255
                x_min = max(0, int(bbox["bbox"][0] * self.image_size[0]))
                y_min = max(0, int(bbox["bbox"][1] * self.image_size[1]))
                x_max = min(self.image_size[0] - 1, int(bbox["bbox"][2] * self.image_size[0]))
                y_max = min(self.image_size[1] - 1, int(bbox["bbox"][3] * self.image_size[1]))
                bbox_mask_window = foreground_mask[y_min:y_max, x_min:x_max]
                foreground_portion = bbox_mask_window.sum() / bbox_mask_window.size
                if foreground_portion < .07:
                    post_processed_results.remove(bbox)
        return post_processed_results

    def load_model(self):
        """
        This function will load the IterDet model with its checkpoints on Crowd Human dataset. The chechpoints and configs
        will be download in "data/iterdet" directory if they do not exists already.
        """
        base_path = "data/iterdet"
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        config_file = os.path.join(base_path, "crowd_human_full_faster_rcnn_r50_fpn_2x.py")
        if not os.path.isfile(config_file):
            url = "https://raw.githubusercontent.com/saic-vul/iterdet/master/" \
                  "configs/iterdet/crowd_human_full_faster_rcnn_r50_fpn_2x.py"
            logging.info(f'config file does not exist under: {config_file}, downloading from {url}')
            wget.download(url, config_file)

        checkpoint_file = os.path.join(base_path, "crowd_human_full_faster_rcnn_r50_fpn_2x.pth")
        if not os.path.isfile(checkpoint_file):
            url = "https://github.com/saic-vul/iterdet/releases/download/v2.0.0/crowd_human_full_faster_rcnn_r50_fpn_2x.pth"
            logging.info(f'checkpoint file does not exist under: {checkpoint_file}, downloading from {url}')
            wget.download(url, checkpoint_file)

        # build the model from a config file and a checkpoint file
        device = self.config.get_section_dict('Teacher')['Device']
        if device == "GPU" and torch.cuda.is_available():
            device = "cuda:0"
        else:
            device = "cpu"
        model = init_detector(config_file, checkpoint_file, device=device)

        return model
