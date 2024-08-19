from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool
from utils.utils import get_os_type


class VolumeLevel(BaseModel):
    volume_level: int = Field(description='Volume value.(The volume level, ranging from 0 to 100)')


class StepVolumeStep(BaseModel):
    step: int = Field(description='Adjustment step size, can be positive (increase volume) '
                                  'or negative (decrease volume)')


@tool('set-volume', args_schema=VolumeLevel)
def set_volume(volume_level: int) -> str:
    """Set the system volume to the specified value."""
    os_type = get_os_type()

    if not (0 <= volume_level <= 100):
        # raise ValueError("音量等级必须在0到100之间。")
        return '音量等级必须在0到100之间'

    if os_type == "macOS":
        import os
        os.system(f"osascript -e 'set volume output volume {volume_level}'")
        return f'音量已经调节到{volume_level}'
    elif os_type == "Windows":
        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        # 将音量转换为PyCaw可接受的范围 [-65.25, 0.0]
        volume_range = volume.GetVolumeRange()
        min_volume = volume_range[0]
        max_volume = volume_range[1]
        adjusted_volume = (volume_level / 100) * (max_volume - min_volume) + min_volume

        volume.SetMasterVolumeLevel(adjusted_volume, None)
        return f'音量已经调节到{volume_level}'
    else:
        # raise EnvironmentError("仅支持macOS和Windows操作系统")
        return 'Unsupported platform'


@tool('adjust-volume', args_schema=StepVolumeStep)
def adjust_volume(step: int) -> str:
    """Adjust the system volume according to the current system volume."""
    os_type = get_os_type()

    if os_type == "macOS":
        import os
        current_volume = int(os.popen("osascript -e 'output volume of (get volume settings)'").read().strip())
        new_volume = max(0, min(100, current_volume + step))
        print(current_volume, new_volume)
        if new_volume == current_volume:
            # print(f"音量已处于边界值({new_volume}%)，无法调整。")
            return f'音量已处于边界值({new_volume}%)，无法调整。'
        else:
            os.system(f"osascript -e 'set volume output volume {new_volume}'")
            # print(f"macOS 当前音量: {new_volume}%")
            return f'当前音量已经调整到了: {new_volume}%'

    elif os_type == "Windows":
        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        current_volume = volume.GetMasterVolumeLevelScalar() * 100
        new_volume = max(0, min(100, current_volume + step))

        if new_volume == current_volume:
            # print(f"音量已处于边界值({new_volume}%)，无法调整。")
            return f'音量已处于边界值({new_volume}%)，无法调整。'
        else:
            # 将音量转换为PyCaw可接受的范围 [-65.25, 0.0]
            volume_range = volume.GetVolumeRange()
            min_volume = volume_range[0]
            max_volume = volume_range[1]
            adjusted_volume = (new_volume / 100) * (max_volume - min_volume) + min_volume

            volume.SetMasterVolumeLevel(adjusted_volume, None)
            # print(f"Windows 当前音量: {new_volume}%")
            return f'当前音量已经调整到了: {new_volume}%'
    else:
        # raise EnvironmentError("仅支持macOS和Windows操作系统。")
        return 'Unsupported platform'


@tool
def mute_volume():
    """Mute system volume"""
    os_type = get_os_type()

    if os_type == "macOS":
        import os

        # macOS mute volume
        os.system("osascript -e 'set volume output muted true'")
    elif os_type == "Windows":
        import ctypes

        # Windows mute volume
        # 使用ctypes调用Windows API来设置音量
        ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)  # 按下Mute键
        ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)  # 释放Mute键
    print(f"System volume muted on {os_type}")
    return '系统音量已经静音了'


@tool
def recover_volume():
    """Restore system volume"""
    os_type = get_os_type()

    if os_type == "macOS":
        import os

        # macOS recover volume
        os.system("osascript -e 'set volume output muted false'")
    elif os_type == "Windows":
        import ctypes

        # Windows recover volume
        # 使用ctypes调用Windows API来设置音量
        ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)  # 按下Mute键
        ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)  # 释放Mute键
    print(f"System volume recover on {os_type}")
    return '系统音量已经恢复了'


if __name__ == '__main__':
    # try:
    #     # 设定系统音量为50%
    #     set_volume.invoke({'volume_level': 30})
    #     print("系统音量已调整。")
    # except Exception as e:
    #     print(f"出现错误: {e}")

    try:
        # 调整音量，每次增加5%
        adjust_volume.invoke({'step': 5})

        # 调整音量，每次减少5%
        # adjust_volume.invoke({'step': -5})

    except Exception as e:
        print(f"出现错误: {e}")
