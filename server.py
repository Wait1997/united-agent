import uvicorn
import time
import json
import asyncio
import argparse

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from langdetect import detect
from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Union

from llm_agent import stdout_result

model_name = 'glm-4'

app = FastAPI()

'''
参数说明：
# CORSMiddleware：指定要添加的中间件类。 CORSMiddleware是用于处理跨域资源共享（CORS）的中间件。
CORS 是一种机制，允许在浏览器中运行的 Web 应用程序访问不同域上的资源。CORSMiddleware 中间件帮助管理跨域请求，并设置相应的 CORS 标头
# allow_origins=["*"]：允许的源（域）列表。在这个例子中，设置为 ["*"] 表示允许来自任何源的请求。
# allow_credentials=True：指示是否允许发送凭据（如 cookies）的请求。
# allow_methods=["*"]：允许的 HTTP 方法列表。在这个例子中，设置为 ["*"] 表示允许所有的 HTTP 方法。
# allow_headers=["*"]：允许的请求标头列表。在这个例子中，设置为 ["*"] 表示允许所有的请求标头。
'''
app.add_middleware(  # 使用 add_middleware 方法向 FastAPI 应用程序添加中间件
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 定义ChatMessage 数据模型
class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


# 定义DeltaMessage 数据模型-->存储流式是输出的对话
class DeltaMessage(BaseModel):
    role: Optional[Literal["user", "assistant", "system"]] = None
    content: Optional[str] = None


# 定义ChatCompletionRequest 数据模型-->储存ChatCompletion的Request
class ChatCompletionRequest(BaseModel):
    model: Optional[str] = model_name
    messages: List[ChatMessage]
    temperature: Optional[float] = None
    max_length: Optional[int] = None
    stream: Optional[bool] = True


# 定义ChatCompletionResponseChoice 数据模型-->储存ChatCompletionResponse的Choice
class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Literal["stop", "length"]


# 定义ChatCompletionResponseStreamChoice数据模型-->储存ChatCompletionResponseStream的Choice
class ChatCompletionResponseStreamChoice(BaseModel):
    index: int
    delta: DeltaMessage
    finish_reason: Optional[Literal["stop", "length"]]


# 定义ChatCompletionResponse数据模型-->储存ChatCompletionResponse的类型
class ChatCompletionResponse(BaseModel):
    model: str
    object: Literal["chat.completion", "chat.completion.chunk"]
    choices: List[Union[ChatCompletionResponseChoice, ChatCompletionResponseStreamChoice]]
    created: Optional[int] = Field(default_factory=lambda: int(time.time()))


# 判断语言
def detect_language(text):
    lang = detect(text)
    if lang == 'zh-cn' or lang == 'zh-tw':
        return True
    else:
        return False


@app.post("/v1/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest):
    if request.messages[-1].role != "user":
        raise HTTPException(status_code=400, detail="Invalid request")
    # 获取user的query
    query = request.messages[-1].content
    # 构建历史记录
    chat_history = []
    history_messages = request.messages[:-1]
    for role, content in history_messages:
        chat_history.append({"role": role, "content": content})

    if request.stream:
        received_value = stdout_result(
            query=query,
            history_messages=history_messages,
            model=request.model,
            streaming=request.stream,
            temperature=request.temperature
        )

        async def event_generator():
            # 定义流式输出的设置
            choice_data = ChatCompletionResponseStreamChoice(
                index=0,
                delta=DeltaMessage(role="assistant"),
                finish_reason=None
            )
            # 将流式输出以ChatCompletionResponse数据模型储存
            chunk = ChatCompletionResponse(model=request.model, choices=[choice_data], object="chat.completion.chunk")
            # 使用yield进行流式输出
            yield "{}".format(json.dumps(chunk.model_dump(exclude_unset=True), ensure_ascii=False))

            start_time = time.time()
            for incremental_text in received_value:
                # if await request.is_disconnected():
                #     print("连接已中断...")
                #     break
                choice_data = ChatCompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(content=incremental_text),
                    finish_reason=None
                )
                chunk = ChatCompletionResponse(
                    model=request.model,
                    choices=[choice_data],
                    object="chat.completion.chunk"
                )
                print(chunk)
                # 使用yield进行流式输出
                yield "{}".format(json.dumps(chunk.model_dump(exclude_unset=True), ensure_ascii=False))
                await asyncio.sleep(0.1)
                print(time.time() - start_time)

            # 全部输出后返回'[DONE]'
            choice_data = ChatCompletionResponseStreamChoice(
                index=0,
                delta=DeltaMessage(),
                finish_reason="stop"
            )
            chunk = ChatCompletionResponse(
                model=request.model,
                choices=[choice_data],
                object="chat.completion.chunk"
            )
            # 使用yield进行流式输出
            yield "{}".format(json.dumps(chunk.model_dump(exclude_unset=True), ensure_ascii=False))
            yield '[DONE]'

        return EventSourceResponse(content=event_generator())
    else:
        received_value = stdout_result(
            query=query,
            history_messages=history_messages,
            model=request.model,
            streaming=request.stream,
            temperature=request.temperature
        )
        choice_data = ChatCompletionResponseChoice(
            index=0,
            message=ChatMessage(role="assistant", content=received_value),
            finish_reason="stop"
        )
        return ChatCompletionResponse(model=request.model, choices=[choice_data], object="chat.completion")


# 主函数入口
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='ip号')
    parser.add_argument('--port', type=int, default=3000,
                        help='端口号')
    args = parser.parse_args()
    # 启动FastAPI应用
    uvicorn.run(app, host=args.host, port=args.port, workers=1)  # 在指定端口和主机上启动应用
