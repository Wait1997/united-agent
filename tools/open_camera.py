from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool
from typing import Callable
import cv2


# class CameraCallback(BaseModel):
#     fn: Callable[[str], None] = Field(description="A function representing the callback function "
#                                                   "returned by the open_camera function")


@tool
def open_camera() -> str:
    """Open the system camera (evoked the system camera)."""

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        # raise IOError("无法打开摄像头")
        return '无法打开摄像头'

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 显示摄像头画面
        cv2.imshow('摄像头', frame)

        # 按下'q'键退出摄像头视图
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放摄像头并关闭窗口
    cap.release()
    cv2.destroyAllWindows()
    return '摄像头已经关闭了'
