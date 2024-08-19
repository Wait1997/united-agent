from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool
from utils.utils import get_os_type


class BrightnessLevel(BaseModel):
    brightness_level: int = Field(description="The brightness value to be set "
                                              "(brightness level, ranging from 0 to 100)")


class StepInput(BaseModel):
    step: int = Field(description="Adjustment step size, can be positive "
                                  "(increase brightness) or negative (decrease brightness)")


@tool('set-brightness', args_schema=BrightnessLevel)
def set_brightness(brightness_level: int) -> str:
    """Sets the system brightness to the specified value."""
    os_type = get_os_type()

    if not (0 <= brightness_level <= 100):
        # raise ValueError("亮度等级必须在0到100之间。")
        return f'亮度等级必须在0到100之间'

    if os_type == "macOS":
        import subprocess
        subprocess.run(["brightness", str(brightness_level / 100)])
        return f'亮度已经设置到了{brightness_level}'
    elif os_type == "Windows":
        import screen_brightness_control as sbc
        sbc.set_brightness(brightness_level)
        return f'亮度已经设置到了{brightness_level}'
    else:
        # raise EnvironmentError("仅支持macOS和Windows操作系统。")
        return 'Unsupported platform'


@tool('adjust-brightness', args_schema=StepInput)
def adjust_brightness(step: int) -> str:
    """Adjust the system brightness according to the current system brightness value."""
    os_type = get_os_type()

    if os_type == "macOS":
        try:
            import subprocess
            # 使用 brightness -l 命令获取亮度信息
            brightness_output = subprocess.run(["brightness", "-l"], capture_output=True, text=True).stdout

            # 提取亮度值，假设亮度值在输出的某一行中，并且以 "brightness" 为关键字
            for line in brightness_output.splitlines():
                if "brightness" in line:
                    current_brightness = float(line.split()[-1])  # 获取行中最后一个元素
                    break
            else:
                # raise ValueError("无法从命令行输出中解析亮度值。")
                return '无法从命令行输出中解析亮度值'

            # 调整亮度
            new_brightness = max(0, min(1, current_brightness + step / 100))

            if new_brightness == current_brightness:
                # print(f"亮度已处于边界值({int(new_brightness * 100)}%)，无法调整。")
                return f"亮度已处于边界值({int(new_brightness * 100)}%)，无法调整。"
            else:
                subprocess.run(["brightness", str(new_brightness)])
                # print(f"macOS 当前亮度: {int(new_brightness * 100)}%")
                return f'亮度已经调节到：{int(new_brightness * 100)}%'

        except Exception as e:
            # print(f"解析亮度值时出错: {e}")
            return f"解析亮度值时出错: {e}"

    elif os_type == "Windows":
        import screen_brightness_control as sbc

        current_brightness = sbc.get_brightness(display=0)[0]  # 获取第一个显示器的亮度
        new_brightness = max(0, min(100, current_brightness + int(step)))
        if new_brightness == current_brightness:
            # print(f"亮度已处于边界值({new_brightness}%)，无法调整。")
            return f"亮度已处于边界值({new_brightness}%)，无法调整。"
        else:
            sbc.set_brightness(new_brightness)
            # print(f"Windows 当前亮度: {new_brightness}%")
            return f'亮度已经调节到: {new_brightness}%'
    else:
        # raise EnvironmentError("仅支持macOS和Windows操作系统。")
        return 'Unsupported platform'


if __name__ == "__main__":
    # try:
    #     # 设定系统亮度为80%
    #     set_brightness.invoke({'brightness_level': 80})
    #
    # except Exception as e:
    #     print(f"出现错误: {e}")

    try:
        # 调整亮度，每次增加5%
        adjust_brightness.invoke({'step': 5})

        # 调整亮度，每次减少5%
        # adjust_brightness.invoke({'step': -5})

    except Exception as e:
        print(f"出现错误: {e}")
