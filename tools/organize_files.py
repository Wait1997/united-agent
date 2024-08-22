"""将桌面最近未使用的文件放在一个temp的文件夹"""
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool
from typing import Literal, List
from utils.utils import get_os_type
import os
import time
import shutil

ONE_DAY = 24 * 60 * 60
allowed_extensions = {
    # 文档文件
    '.txt', '.docx', '.md', '.xlsx', '.pdf', '.pptx',
    # 图片文件
    '.jpg', '.jpeg', '.png', '.gif', '.bmp',
    # 视频文件
    '.mp4', '.mkv', '.avi', '.mov', '.wmv'
}


class RecentDays(BaseModel):
    days: int = Field(description='Number of days (Recent unused days).')


def get_desktop_path(system_type: Literal['Windows', 'macOS']) -> str:
    """获取桌面路径"""
    if system_type == 'Windows':
        return os.path.join(os.path.expanduser("~"), "Desktop")
    elif system_type == 'macOS':  # macOS 的系统类型是 'Darwin'
        return os.path.join(os.path.expanduser("~"), "Desktop")
    else:
        raise EnvironmentError(f"该系统 {system_type} 暂不支持")


def get_unused_files_and_folders(desktop_path: str, days: int = 10) -> List[str]:
    """获取指定天数内未使用的文件和文件夹"""
    unused_items = []
    cutoff_time = time.time() - days * ONE_DAY

    # 获取指定目录下的文件以及文件夹
    for item in os.listdir(desktop_path):
        item_path = os.path.join(desktop_path, item)

        # 处理文件
        if os.path.isfile(item_path):
            file_extension = os.path.splitext(item)[-1].lower()  # 获取文件扩展名并转为小写
            if file_extension in allowed_extensions:
                if not os.path.exists(item_path):  # 确保路径存在
                    continue
                # 指定文件或目录的最后访问时间 单位s
                # last_access_time = os.path.getatime(item_path)
                # 修改时间 (getmtime) 更新的时机是文件内容发生了变更
                last_modify_time = os.path.getmtime(item_path)
                date = time.localtime(last_modify_time)
                format_date = time.strftime('%Y-%m-%d %H:%M:%S', date)
                print(format_date, item_path)

                if last_modify_time < cutoff_time:
                    unused_items.append(item_path)
        # 处理文件夹
        if os.path.isdir(item_path):
            if not os.path.exists(item_path):  # 确保路径存在
                continue
            # 指定文件或目录的最后访问时间 单位s
            # last_access_time = os.path.getatime(item_path)
            # 修改时间 (getmtime) 更新的时机是文件内容发生了变更
            last_modify_time = os.path.getmtime(item_path)
            date = time.localtime(last_modify_time)
            format_date = time.strftime('%Y-%m-%d %H:%M:%S', date)
            print(format_date, item_path)

            if last_modify_time < cutoff_time:
                unused_items.append(item_path)

    return unused_items


def create_temp_folder(desktop_path: str) -> str:
    """在桌面上创建 temp 文件夹"""
    temp_folder_path = os.path.join(desktop_path, "temp")
    if not os.path.exists(temp_folder_path):
        os.makedirs(temp_folder_path)
    return temp_folder_path


def move_items_to_temp(unused_items: List[str], temp_folder_path: str):
    """将未使用的文件和文件夹移动到 temp 文件夹"""
    for item in unused_items:
        item_name = os.path.basename(item)
        destination = os.path.join(temp_folder_path, item_name)
        if os.path.exists(destination):
            continue  # 跳过已经存在的文件或文件夹

        try:
            shutil.move(item, destination)
        except PermissionError:
            raise PermissionError


@tool('organize-files', args_schema=RecentDays)
def organize_files(days: int):
    """
    Place the files and folders on the desktop that have not been used in the last few days in a temp folder
    (Organize desktop files and folders into temp folders according to the number of days they have not been used).
    """

    os_type = get_os_type()
    try:
        desktop_path = get_desktop_path(os_type)
        unused_items = get_unused_files_and_folders(desktop_path, days=days)

        if not unused_items:
            return f"没有最近 {days} 天未使用的文件或文件夹"

        temp_folder_path = create_temp_folder(desktop_path)
        move_items_to_temp(unused_items, temp_folder_path)
        return f'已将最近 {days} 天未使用的文件和文件夹移动到 {temp_folder_path}'

    except PermissionError as e:
        return f'没有权限访问文件或目录：{e}'
    except EnvironmentError as e:
        return e


if __name__ == '__main__':
    print(organize_files.name)
    # 最近3天
    print(organize_files.invoke({'days': 3}))
