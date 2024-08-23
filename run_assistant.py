import os
import ctypes
from ctypes import cdll
from ctypes import Structure
from time import sleep
import asyncio

DLL_FILE = 'flowy.dll'
DLL_PATH = os.path.join(os.path.dirname(__file__), DLL_FILE)


class Model(Structure):
    _fields_ = [("name", ctypes.c_char_p),
                ("endpoint", ctypes.c_char_p),
                ("apikey", ctypes.c_char_p)]


class ChatMessage(Structure):
    _fields_ = [("role", ctypes.c_int), ("content", ctypes.c_char_p)]


# 定义函数类型
ret_type = None
arg_types = (ctypes.c_int, ctypes.c_char_p)
call_type = ctypes.CFUNCTYPE(ret_type, *arg_types)


class ChatInput(Structure):
    _fields_ = [("agentId", ctypes.c_int),
                ("modelId", ctypes.c_int),
                ("historyMessages", ctypes.POINTER(ChatMessage)),
                ("historyCount", ctypes.c_int),
                ("message", ctypes.c_char_p),
                ("call", call_type), ]


class CallResult(Structure):
    _fields_ = [("success", ctypes.c_int), ("message", ctypes.c_char_p)]


flowyDLL = cdll.LoadLibrary(DLL_PATH)


# def message_response(status,msg):
#     print(msg.decode("utf-8"))


def init_flowy_env():
    flowyDLL.InitEnv.restype = ctypes.POINTER(CallResult)
    result = flowyDLL.InitEnv()

    return result[0].success == 0
    # flowyDLL.FreeStr(err_message)


def add_model(name, endpoint, apikey):
    model = Model()
    model.name = ctypes.c_char_p(name.encode("utf-8"))
    model.apikey = ctypes.c_char_p(apikey.encode("utf-8"))
    model.endpoint = ctypes.c_char_p(endpoint.encode("utf-8"))

    mid = flowyDLL.AddOpenAIChatModel(model)

    return mid


def chat_with_pc_assistant(model_id, message, msg_history, stream_callback):
    """PC助手对话
    :param model_id: 模型id
    :param message: 消息
    :param msg_history: 历史对话 [{"role":0,"content":"消息"}] 0 system,1 user,2 assistant
    :param stream_callback: 流式输出回调  def callback(status,msg),status 输出状态 status 0:splash 1:increment 2:finish,msg消息的bytes 需要decode("utf-8")
    :return: 请求成功或失败
    """
    chatInput = ChatInput()

    chatInput.agentId = ctypes.c_int(0)
    chatInput.modelId = ctypes.c_int(model_id)

    history = (ChatMessage * len(msg_history))()
    for i in range(len(msg_history)):
        history[i] = ChatMessage()
        raw_history = msg_history[i]
        history[i].role = ctypes.c_int(raw_history.role)
        history[i].content = ctypes.c_char_p(ctypes.c_char_p(raw_history.content.encode("utf-8")))

    chatInput.historyCount = ctypes.c_int(len(msg_history))
    chatInput.message = ctypes.c_char_p(message.encode("utf-8"))

    chatInput.call = call_type(stream_callback)

    flowyDLL.ChatWithPCAssistant.restype = ctypes.POINTER(CallResult)

    result = flowyDLL.ChatWithPCAssistant(chatInput)

    return result[0].success == 0


def chat_with_weekly_assistant(model_id, message, msg_history, stream_callback):
    """周报助手对话
    :param model_id: 模型id
    :param message: 消息
    :param msg_history: 历史对话 [{"role":0,"content":"消息"}] 0 system,1 user,2 assistant
    :param stream_callback: 流式输出回调  def callback(status,msg),status 输出状态 status 0:splash 1:increment 2:finish,msg消息的bytes 需要decode("utf-8")
    :return: 请求成功或失败
    """
    chatInput = ChatInput()

    chatInput.agentId = ctypes.c_int(0)
    chatInput.modelId = ctypes.c_int(model_id)

    history = (ChatMessage * len(msg_history))()
    for i in range(len(msg_history)):
        history[i] = ChatMessage()
        raw_history = msg_history[i]
        history[i].role = ctypes.c_int(raw_history.role)
        history[i].content = ctypes.c_char_p(ctypes.c_char_p(raw_history.content.encode("utf-8")))

    chatInput.historyCount = ctypes.c_int(len(msg_history))
    chatInput.message = ctypes.c_char_p(message.encode("utf-8"))

    chatInput.call = call_type(stream_callback)

    flowyDLL.ChatWithWeeklyReportAssistant.restype = ctypes.POINTER(CallResult)

    result = flowyDLL.ChatWithWeeklyReportAssistant(chatInput)

    return result[0].success == 0


def chat_with_mindmap_assistant(model_id, message, msg_history):
    """思维导图助手对话
    :param model_id: 模型id
    :param message: 消息
    :param msg_history: 历史对话 [{"role":0,"content":"消息"}] 0 system,1 user,2 assistant
    :param stream_callback: 流式输出回调  def callback(status,msg),status 输出状态 status 0:splash 3:full,msg消息的bytes 需要decode("utf-8")
    :return: 请求成功或失败
    """
    chatInput = ChatInput()

    chatInput.agentId = ctypes.c_int(0)
    chatInput.modelId = ctypes.c_int(model_id)

    history = (ChatMessage * len(msg_history))()
    for i in range(len(msg_history)):
        history[i] = ChatMessage()
        raw_history = msg_history[i]
        history[i].role = ctypes.c_int(raw_history.role)
        history[i].content = ctypes.c_char_p(ctypes.c_char_p(raw_history.content.encode("utf-8")))

    chatInput.historyCount = ctypes.c_int(len(msg_history))
    chatInput.message = ctypes.c_char_p(message.encode("utf-8"))

    chatInput.call = call_type()

    flowyDLL.ChatWithMindMapAssistant.restype = ctypes.POINTER(CallResult)

    result = flowyDLL.ChatWithMindMapAssistant(chatInput)

    if result[0].success == 0:
        return result[0].message.decode("utf-8")
    else:
        return ""


def chat_with_meeting_minutes_assistant(model_id, message):
    """会议纪要助手对话
    :param model_id: 模型id
    :param message: 消息
    :param msg_history: 历史对话 [{"role":0,"content":"消息"}] 0 system,1 user,2 assistant
    :param stream_callback: 流式输出回调  def callback(status,msg),status 输出状态 status 0:splash 3:full,msg消息的bytes 需要decode("utf-8")
    :return: 请求成功或失败
    """
    chatInput = ChatInput()

    chatInput.agentId = ctypes.c_int(0)
    chatInput.modelId = ctypes.c_int(model_id)

    chatInput.historyCount = ctypes.c_int(0)
    chatInput.message = ctypes.c_char_p(message.encode("utf-8"))

    chatInput.call = call_type()

    flowyDLL.ChatWithMeetingMinutesAssistant.restype = ctypes.POINTER(CallResult)

    result = flowyDLL.ChatWithMeetingMinutesAssistant(chatInput)

    if result[0].success == 0:
        return result[0].message.decode("utf-8")
    else:
        return ""


def chat_with_agents(model_id, message, msg_history, stream_callback):
    """PC助手,脑图助手,周报助手统一入口
    :param model_id: 模型id
    :param message: 消息
    :param msg_history: 历史对话 [{"role":0,"content":"消息"}] 0 system,1 user,2 assistant
    :param stream_callback: 流式输出回调  def callback(status,msg),status 输出状态 status 0:splash 1:increment 2:finish，3:full,msg消息的bytes 需要decode("utf-8")
    :return: 请求成功或失败
    """
    chatInput = ChatInput()

    chatInput.agentId = ctypes.c_int(0)
    chatInput.modelId = ctypes.c_int(model_id)

    history = (ChatMessage * len(msg_history))()
    for i in range(len(msg_history)):
        history[i] = ChatMessage()
        raw_history = msg_history[i]
        history[i].role = ctypes.c_int(raw_history.role)
        history[i].content = ctypes.c_char_p(ctypes.c_char_p(raw_history.content.encode("utf-8")))

    chatInput.historyCount = ctypes.c_int(len(msg_history))
    chatInput.message = ctypes.c_char_p(message.encode("utf-8"))

    chatInput.call = call_type(stream_callback)

    flowyDLL.ChatWithAgents.restype = ctypes.POINTER(CallResult)

    result = flowyDLL.ChatWithAgents(chatInput)
    # print(result[0].message.decode("utf-8"))
    return result[0].success == 0


if __name__ == '__main__':
    all_text = ''

    #初始化环境
    init_flowy_env()
    # 添加模型
    mid = add_model("deepseek-chat", "https://api.deepseek.com", "sk-8f229cb93e78416e96430020d260f2b7")


    #流式输出回调
    def stream_print(status, msg_fragment):
        # status 0:splash 1:increment 2:finish
        global all_text
        # print(msg_fragment.decode("utf-8"))
        all_text += msg_fragment.decode("utf-8")
        print(all_text)


    r = chat_with_agents(mid, "音量调整到20%", [], stream_print)
    # print(r)

    # chat_with_pc_assistant(mid,"音量调整到50%",[],stream_print)
    # chat_with_weekly_assistant(mid, "周一入职，周二对接之前离职人的项目，周三开始熟悉代码，周四将项目跑起来了了，周五摸鱼了一天", [], stream_print)
    msg = """
        学习C语言的课程列表涵盖了从基础到高级的各个方面，包括但不限于：
        基础语法和编程环境设置‌：课程从C语言的基础语法开始，介绍如何安装编程软件、创建文件，以及编写和运行第一个C语言程序。这部分内容旨在让学生掌握C语言编程的基本环境和步骤‌1。
        数据类型和变量‌：课程详细解释了C语言中的基本数据类型，如整型、实型、字符型等，以及如何定义和使用变量。此外，还涉及数据的存储方式，如二进制、位与字节，以及算术运算符的使用‌12。
        输入输出操作‌：课程讨论了如何在C语言中进行数据的输入和输出，包括使用printf和scanf函数等‌13。
        控制流语句‌：涉及条件语句（如if-else）、多分支语句、循环语句（如for、while、do-while）以及goto语句的学习。这些语句用于控制程序的执行流程‌45。
        函数‌：介绍如何定义和调用函数，包括参数传递（值传递、引用传递）、函数指针等‌5。
        数组和指针‌：讲解一维和多维数组的使用，以及指针的概念和语法。还包括指针运算和动态内存分配的内容‌5。
        结构体和联合体‌：介绍结构体的定义和成员访问，以及联合体的概念‌5。
        文件处理‌：讨论如何进行文件操作，包括文件的打开、关闭、读写等，以及文件模式（读、写、追加）的学习‌5。
        高级主题‌：包括预处理指令、位运算、内存管理、异常处理等高级主题的讲解‌5。
        项目实战‌：通过小型命令行工具开发和数据结构实现（如链表、栈、队列）等项目实战，加深学生对C语言的理解和应用‌5。
        此外，还有一些学习资源推荐，如在线课程和教程，以及相关的参考书籍，如《C Primer Plus》、《深入理解计算机系统》等，以帮助学生更系统地学习和掌握C语言‌
        
        帮我将以上文本生成脑图
    """

    # chat_with_agents(mid, msg,[], stream_print)
    # mindmapStr = chat_with_mindmap_assistant(mid,msg,[])
    #
    # print(mindmapStr)
    #
    # meeting_result= chat_with_meeting_minutes_assistant(mid,msg)
    # print(meeting_result)

    #sleep(1000)
