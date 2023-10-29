from celery import shared_task
from weapondetectapp.utils import TerroristDetector


@shared_task
def process_predict_video(video_path):
    detector = TerroristDetector()
    detector.predict_video_and_draw_boxes_on_existing_video(video_path)
    