import os
from typing import List, Dict
from dataclasses import dataclass, field

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
    path: Path to the image
    name_file: Image name
    cls_names: Dict of classes and their names

    boxes: List of bounding box objects
    save_dir: Path to the folder where the image with the bounding box will be saved
    """
    path: str
    name_file: str
    cls_names: Dict[int, str]

    boxes: List[BoxPredict] = field(default_factory=list)
    save_dir: str | None = field(default=None)


class TerroristDetector:
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']

    def __init__(self) -> None:
        self.__model = YOLO('/home/poryadok/Projects/DATASET_FINISH/weights/weights/best.pt')
        self.conf: float = 0.6  # confidence threshold

        self.save_txt: bool = True  # save labels to *.txt
        self.save_conf: bool = True  # save confidences in --save-txt labels
        self.save: bool = True  # save inference images

        self.augment: bool = True  # augmented inference

        self.line_width: int = 2  # bounding box thickness (pixels)

    def predict(self, file_path: str | List[str]) -> List:
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
                save=True,

                augment=self.augment,

                line_width=self.line_width,
            )
            return results

        except Exception as e:
            print(f'File cannot be read: {e}')
            return []

    def sort_folder(self, path_with_data: str) -> List:
        """
        Gets all images from the folder and predicts them.

        Args:
            path_with_data: Path to the folder with images.

        Returns:
            List of source predict objects.
        """
        predict_info = []
        files = os.listdir(path_with_data)
        files = [file for file in files if os.path.splitext(
            file)[1].lower() in self.IMAGE_EXTENSIONS]
        for file in files:
            image_path = os.path.join(path_with_data, file)
            image_info = self.predict(image_path)
            if image_info:
                predict_info.append(image_info)

        return predict_info

    def convert_to_predict_objects(self, source_predict_list: List) -> List[ImagePredict]:
        """
        Gets prediction objects from source predict objects.

        Args:
            source_predict_list: List of source predict objects.

        Returns:
            List of ImagePredict objects.
        """

        imagePredict_objects: List[ImagePredict] = []
        # Iterate all source predict objects
        for source_predict in source_predict_list:
            object = source_predict[0]

            # Get attributes from source predict object
            path = object.path
            name_file = os.path.basename(path)
            cls_names = object.names

            imagePredict = ImagePredict(
                path=path,
                name_file=name_file,
                cls_names=cls_names,
            )

            # Get information about saving the image with the bounding box if it is available
            if hasattr(object, 'save_dir'):
                imagePredict.save_dir = object.save_dir

            # Creatint bounding box objects
            boxes = object.boxes
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
            imagePredict_objects.append(imagePredict)

        return imagePredict_objects

    def predict_folder(self, path_with_data: str) -> List[ImagePredict]:
        """
        Predicts all images from the folder and returns prediction objects.

        Args:
            path_with_data: Path to the folder with images.

        Returns:
            List of ImagePredict objects.
        """

        source_predict_list = self.sort_folder(path_with_data)
        imagePredict_objects = self.convert_to_predict_objects(
            source_predict_list)
        return imagePredict_objects


def main():
    model = TerroristDetector()

    # Set parameters
    model.conf = 0.6
    model.save_txt = True
    model.save_conf = True
    model.save = True
    model.augment = True
    model.line_width = 2

    list_predict = model.predict_folder(
        '/home/poryadok/Projects/DATASET_FINISH/5_00_DROBOVIKI/')

    for predict in list_predict:
        print(predict.path)
        print(predict.name_file)
        print(predict.cls_names)
        print(predict.save_dir)
        print(predict.boxes)
        print('\n')


if __name__ == "__main__":
    main()
