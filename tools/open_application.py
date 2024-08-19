"""打开系统程序"""
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool
import os
import subprocess
from utils import get_os_type, BasicMatcher


class AppNameInput(BaseModel):
    app_name: str = Field(description="The name of the app")


@tool("open-application", args_schema=AppNameInput)
def open_application(app_name: str) -> str:
    """Open the specified app on your computer."""

    system_platform = get_os_type()

    basic_matcher = BasicMatcher()
    matched_name = basic_matcher.match_app(app_name)
    # 正则匹配重新赋值
    if matched_name:
        app_name = matched_name

    if system_platform == "macOS":
        app_path = f"/Applications/{app_name}.app"
        if os.path.exists(app_path):
            subprocess.run(["open", app_path])
            return f'{app_name}已经打开了'
        else:
            # raise FileNotFoundError(f"Application {app_name} not found in /Applications")
            # 这里需要给llm一个返回值
            return f'Application {app_name} not found in /Applications'

    elif system_platform == "Windows":
        try:
            subprocess.run(["start", app_name], shell=True)
            return f'{app_name}已经打开了'
        except Exception as e:
            # raise RuntimeError(f"Failed to open {app_name}: {e}")
            # 这里需要给llm一个返回值
            return f'Failed to open {app_name}: {e}'

    else:
        # raise EnvironmentError("Unsupported platform")
        return 'Unsupported platform'


@tool
def open_calc():
    """Open the calculator on your computer (Calculator in computer)."""

    system_platform = get_os_type()

    if system_platform == "macOS":
        try:
            subprocess.Popen(['open', '-a', 'Calculator'])
            return '计算器已打开'
        except FileNotFoundError:
            return '无法找到计算器程序'
    elif system_platform == "Windows":
        try:
            subprocess.Popen('calc.exe')
            return '计算器已打开'
        except FileNotFoundError:
            return '无法找到计算器程序'


if __name__ == '__main__':
    print(open_application.name)
    result = open_application.invoke('vscode')
    print(result)
