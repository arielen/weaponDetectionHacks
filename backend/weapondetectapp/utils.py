import io
import os
import cv2
import numpy as np
from typing import List, Dict, Generator
from dataclasses import dataclass, field
from PIL import Image, ImageDraw, ImageFont

from ultralytics import YOLO


@dataclass
class BoxPredict:
    """
    cls: Box class
    conf: Confidence score

    xyxy: Coordinates of two floats of the bounding boxes
    """
    cls: float
    conf: float

    xyxy: List[float]


@dataclass
class ImagePredict:
    """
    source_predict: Predict source object

    path: Path to the image
    name_file: Image name
    cls_names: Dict of classes and their names

    boxes: List of bounding box objects
    save_dir: Path to the folder where the image with the bounding box will be saved
    """
    source_predict: object

    path: str
    name_file: str
    cls_names: Dict[float, str]

    boxes: List[BoxPredict] = field(default_factory=list)
    save_dir: str | None = field(default=None)


class TerroristDetector:
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png',]

    CLASS_NAMES = {
        0: 'person',
        1: 'gun',
        2: 'person'
    }

    def __init__(self, model_path: str = 'weapondetectapp/weights/best.pt') -> None:
        self.__model = YOLO(model_path)
        self.conf: float = 0.25  # confidence threshold

        self.save_txt: bool = False  # save labels to *.txt
        self.save_conf: bool = False  # save confidences in --save-txt labels
        self.save: bool = False

        self.augment: bool = False  # augmented inference

        self.line_width: int = 2  # bounding box thickness (pixels)

    def __predict(self, file_path: str) -> List:
        """
        Predicts image class and returns prediction info.

        Args:
            file_path: Path to the image.

        Returns:
            Predict source object or empty list if the file cannot be read.

        Raises:
            Exception: If the file cannot be read.
        """
        try:
            results = self.__model(
                file_path,
                conf=self.conf,

                save_txt=self.save_txt,
                save_conf=self.save_conf,
                save=self.save,

                augment=self.augment,

                line_width=self.line_width,
            )
            return results

        except Exception as e:
            print(f'File cannot be read: {e}')
            return []

    def predict(self, file_path: str) -> ImagePredict:
        """
        Get information about the image and its bounding box.

        Args:
            file_path: Path to the file.

        Returns:
            Image predict object.
        """
        source_predict = self.__predict(file_path)

        object_ = source_predict[0]

        # Get attributes from source predict object
        path = object_.path
        name_file = os.path.basename(path)
        cls_names = object_.names

        imagePredict = ImagePredict(
            source_predict=object_,
            path=path,
            name_file=name_file,
            cls_names=cls_names,
        )

        # Get information about saving the image with the bounding box if it is available
        if hasattr(object_, 'save_dir'):
            imagePredict.save_dir = object_.save_dir

        # Creatint bounding box objects
        boxes = object_.boxes
        box_objects: List[BoxPredict] = []
        for box in boxes:
            try:
                # Get attributes from bounding box object
                cls = box.cls.item()
                conf = box.conf.item()
                xyxy = box.xyxy.tolist()[0]

                box_objects.append(
                    BoxPredict(
                        cls=cls,
                        conf=conf,
                        xyxy=xyxy
                    )
                )
            except Exception as e:
                print(e)

        imagePredict.boxes = box_objects
        return imagePredict

    def predict_folder_with_images(self, path_with_data: str) -> Generator[ImagePredict, None, None]:
        """
        Predicts classes for all images in a folder.

        Args:
            path_with_data: Path to a folder with images.

        Returns:
            List of predict source objects or empty list if the folder is empty.

        Raises:
            Exception: If the folder is empty.
        """

        file_list = os.listdir(path_with_data)
        image_list = [file for file in file_list if os.path.splitext(
            file)[1].lower() in self.IMAGE_EXTENSIONS]

        if len(image_list) == 0:
            raise Exception('Folder is empty')

        for image in image_list:
            image_path = os.path.join(path_with_data, image)
            yield self.predict(image_path)

    def draw_bounding_box(self, image_predict: ImagePredict) -> io.BytesIO:
        """
        Get image with bounding box and label in byte stream.

        Args:
            image_predict: Image predict object.

        Returns:
            Image with bounding box and label in byte stream.
        """
        try:
            image = Image.open(image_predict.path)
        except:
            image_array: np.ndarray = image_predict.source_predict.orig_img
            image = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)

        # Open the image
        with image as img:
            # Create a drawing context
            draw = ImageDraw.Draw(img)

            # Draw each bounding box
            for box in image_predict.boxes:

                if box.cls == 0:
                    color_box = 'purple'

                elif box.cls == 1:
                    color_box = 'red'

                elif box.cls == 2:
                    color_box = 'green'

                else:
                    color_box = 'white'

                # Extract the coordinates
                x1, y1, x2, y2 = box.xyxy

                # Draw the box
                draw.rectangle((x1, y1, x2, y2),
                               outline=color_box, width=self.line_width)

                # Label the box
                text = f'{image_predict.cls_names[box.cls]} {box.conf:.2f}'
                text = text[:1].upper() + text[1:]
                x_text = x1 + self.line_width
                y_text = y1 + self.line_width

                draw.text(
                    (x_text, y_text), text, fill=color_box, width=self.line_width*2,
                    font=ImageFont.truetype("weapondetectapp/weights/arial.ttf", 20), fill_opacity=1,
                )

            # Save the image to a byte stream
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG')
            buffer.seek(0)

            return buffer

    def save_image_from_buffer(self, buffer: io.BytesIO, path_to_save: str) -> None:
        """
        Save image from byte stream.

        Args:
            buffer: Image in byte stream.
            path_to_save: Path to save the image.
        """
        with open(path_to_save, 'wb') as f:
            f.write(buffer.read())

    def predict_and_draw_boxes_on_existing_image(self, path_to_image: str) -> None:
        """
        Draw bounding boxes on existing image.

        Args:
            path_to_image: Path to the image.
        """
        image_predict = self.predict(path_to_image)
        buffer = self.draw_bounding_box(image_predict)
        self.save_image_from_buffer(buffer, path_to_image)

    def predict_video_and_draw_boxes_on_existing_video(self, path_to_video: str) -> None:
        """
        Draw bounding boxes on existing video and save.

        Args:
            path_to_video: Path to the video.
        """

        new_name = os.path.basename(path_to_video)
        video_path = os.path.join(os.path.dirname(
            path_to_video), f'new_{new_name}')

        # Create a video capture object
        cap = cv2.VideoCapture(path_to_video)

        # Get the video's frame rate
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Get the video's frame size
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Create a video writer object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

        num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Read the video
        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                break

            # Convert the frame to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert the frame to Image
            frame = Image.fromarray(frame)

            # Predict the classes
            frame_predict = self.predict(frame)

            # Draw the bounding boxes
            buffer = self.draw_bounding_box(frame_predict)

            # Convert the byte stream to Image
            buffer = Image.open(buffer)

            src = np.array(buffer)

            # Convert the frame back to OpenCV format
            frame = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)

            # Write the frame to the output video file
            out.write(frame)

            num_frames -= 1

        # Release the video capture and writer objects
        cap.release()
        out.release()

        # Delete the original video and rename the new one
        os.remove(path_to_video)
        os.rename(video_path, path_to_video)
