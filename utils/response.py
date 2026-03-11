# 成功响应结果的封装

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

# 通用响应结果封装
# 所需参数：
# message--响应结果信息
# data--响应结果数据，默认为None
def success_response(message: str = "success", data = None):
    content = {
        "code": 200,
        "message": message,
        "data": data
    }
    # 目标：无论什么类型的data，都能转换成JSON格式
    # jsonable_encoder()，把封装的content翻译为JSON格式并定义content接收
    # JSONResponse()，返回JSON格式的HTTP响应
    return JSONResponse(content=jsonable_encoder(content))
