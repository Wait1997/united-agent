from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent, create_react_agent
from langchain_core.callbacks.manager import CallbackManager
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate
)

from tools import (
    WriteFilesTool,
    set_brightness,
    adjust_brightness,
    set_volume,
    adjust_volume,
    mute_volume,
    recover_volume,
    open_calc,
    open_application,
    organize_files
)
from utils import transform_messages_type, ChatMessage

from typing import Optional, List
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

model_name = 'glm-4'
openai_api_base = 'https://open.bigmodel.cn/api/paas/v4/'
zhipu_key = os.environ['ZHIPUAI_API_KEY']
model_temperature = 0.95


# 获取所有工具集
def get_tools(tool=None) -> List:
    tools = [
        set_volume,
        adjust_volume,
        mute_volume,
        recover_volume,
        open_calc,
        open_application,
        set_brightness,
        adjust_brightness,
        organize_files,
        WriteFilesTool(),
    ]
    if tool:
        tools.append(tool)
    return tools


# 加载prompt
def load_prompt(prompt_type: str = None, custom_prompt=None):
    if custom_prompt:
        return custom_prompt

    from langchain import hub
    if not prompt_type:
        prompt_type = "hwchase17/openai-tools-agent"
        prompt = hub.pull(prompt_type)
    else:
        prompt = hub.pull(prompt_type)
    return prompt


# 创建代理执行器
def executor_llm_agent(
        model: Optional[str] = model_name,
        streaming: Optional[bool] = True,
        temperature: Optional[float] = model_temperature,
        **kwargs):
    # 流式输出
    if streaming:
        llm = ChatOpenAI(
            temperature=temperature,
            model=model,
            api_key=zhipu_key,
            base_url=openai_api_base,
            streaming=streaming,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
        )
    else:
        llm = ChatOpenAI(
            temperature=temperature,
            model=model,
            api_key=zhipu_key,
            base_url=openai_api_base
        )

    # agent = create_react_agent(llm, tools, prompt)
    # create_tool_calling_agent 使用其他的 会导致tool中参数不能正常输入
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template('You are a helpful assistant'),
            MessagesPlaceholder(variable_name='chat_history', optional=True),
            HumanMessagePromptTemplate.from_template('{input}'),
            MessagesPlaceholder(variable_name='agent_scratchpad')
        ]
    )
    agent = create_tool_calling_agent(llm, get_tools(), load_prompt(custom_prompt=chat_prompt))

    # 代理执行器
    def agent_executor_option(verbose: bool = True, handle_parsing_errors: bool = True):
        agent_executor = AgentExecutor(
            agent=agent,
            tools=get_tools(),
            verbose=verbose,
            handle_parsing_errors=handle_parsing_errors
        )
        return agent_executor

    agent_executor = agent_executor_option(verbose=True)

    return agent_executor


def stdout_result(
        query: str,
        history_messages: Optional[List[ChatMessage]] = None,
        model: Optional[str] = model_name,
        streaming: Optional[bool] = True,
        temperature: Optional[float] = model_temperature,
        **kwargs
):
    if not temperature:
        temperature = model_temperature

    agent_with_chat_history = executor_llm_agent(
        model=model,
        temperature=temperature,
        streaming=streaming,
        **kwargs
    )

    # 获取历史消息
    chat_history = []
    if history_messages:
        chat_history = transform_messages_type(history_messages=history_messages)

    received_value = agent_with_chat_history.invoke({'input': query, 'chat_history': chat_history})
    return received_value['output']


if __name__ == '__main__':
    agent_with_chat_history = executor_llm_agent(streaming=False)
    # result = agent_with_chat_history.invoke({'input': '帮我把 Visual Studio Code 打开'})
    # result = agent_with_chat_history.invoke({'input': '帮我把QQ音乐打开'})
    # result = agent_with_chat_history.invoke({'input': '帮我把 Visual Studio Code 打开,并且系统的亮度设置到50'})
    # result = agent_with_chat_history.invoke({'input': '帮我写一份pytorch简单的使用教程，需要把内容写到指定的markdown文件中'})
    # result = agent_with_chat_history.invoke({'input': '帮我把系统音量调小', 'chat_history': []})
    # result = agent_with_chat_history.invoke({'input': '帮我整理最近7天未使用的文件', 'chat_history': []})
    # result = agent_with_chat_history.invoke({'input': '帮我把计算器打开', 'chat_history': []})
    # result = agent_with_chat_history.invoke({
    #     'input': '帮我介绍一下google公司，需要800字左右；并且要求你按照word文档的格式写入到文件中，输入的内容能够符合正常word文档的规范',
    #     'chat_history': []}
    # )
    result = agent_with_chat_history.invoke({'input': '你好'})
    print(result)
