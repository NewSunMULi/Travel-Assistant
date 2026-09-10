# dify.py
import json
import os
from datetime import date
from typing import Any, Dict

import requests
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import dotenv

dotenv.load_dotenv("local.env.example")
# ============ 配置 ============
DIFY_API_BASE = os.environ.get("DIFY_API_BASE", "https://api.dify.ai/v1").rstrip("/")
DIFY_API_KEY = os.environ.get("DIFY_API_KEY", "").strip()

router = APIRouter()


# ============ 请求模型 ============

class TravelPlanRequest(BaseModel):
    """旅行规划请求 —— 与用户输入字段一一对应。

    示例：
    {
        "destination": "昆明",
        "departure": "-",
        "days": 2,
        "people": "2",
        "budget": "3000",
        "style": "休闲",
        "special_request": "帮我安排完整行程",
        "start_date": "2026-09-11"
    }
    """
    destination: str = Field(..., description="目的地，如 昆明")
    departure: str = Field("-", description="出发地，'-' 表示未指定/当地出发")
    days: int = Field(..., ge=1, description="旅行天数")
    people: str = Field(..., description="出行人数")
    budget: str = Field(..., description="总预算（元）")
    style: str = Field("休闲", description="旅行风格，如 休闲/特种兵/亲子")
    special_request: str = Field("", description="特殊需求/备注")
    start_date: date = Field(..., description="出发日期，YYYY-MM-DD")
    user: str = Field("default-user", description="Dify 用户标识")

    def to_dify_inputs(self) -> Dict[str, Any]:
        """组装成 Dify 工作流的 inputs（字段名与 Dify 开始节点变量保持一致）。"""
        return {
            "destination": self.destination,
            "departure": self.departure,
            "days": self.days,
            "people": self.people,
            "budget": self.budget,
            "style": self.style,
            "special_request": self.special_request,
            "start_date": self.start_date.isoformat(),
        }


class WorkflowRequest(BaseModel):
    """原始透传模式：兼容旧的前端调用（任意 inputs 直接转发）。"""
    inputs: Dict[str, Any] = Field(default_factory=dict)
    query: str = ""
    user: str = "default-user"


# ============ Dify 流式调用 ============

def stream_dify_workflow(inputs: Dict[str, Any], user: str = "default-user"):
    """调用 Dify 工作流 streaming 接口，逐条 yield SSE 数据。"""
    if not DIFY_API_KEY:
        err = {
            "event": "error",
            "stage": "配置错误",
            "error": "环境变量 DIFY_API_KEY 未设置",
        }
        yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"
        return

    url = f"{DIFY_API_BASE}/workflows/run"
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "inputs": inputs,
        "response_mode": "streaming",
        "user": user,
    }

    try:
        with requests.post(url, json=body, headers=headers, stream=True, timeout=120) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data:"):
                    continue
                data_str = line[len("data:"):].strip()
                if not data_str:
                    continue
                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                event = data.get("event")
                out = {"event": event}

                # 工作流开始
                if event == "workflow_started":
                    out["stage"] = "工作流开始"
                    out["workflow_run_id"] = data.get("workflow_run_id")

                # 节点开始：报告阶段名
                elif event == "node_started":
                    node = data.get("data", {})
                    out["stage"] = f"节点开始：{node.get('title', '')}"
                    out["node_type"] = node.get("node_type")
                    out["node_id"] = node.get("node_id")

                # 节点结束：报告结果
                elif event == "node_finished":
                    node = data.get("data", {})
                    out["stage"] = f"节点结束：{node.get('title', '')}"
                    out["status"] = node.get("status")
                    out["outputs"] = node.get("outputs")

                # LLM 文本流式输出
                elif event == "text_chunk":
                    out["stage"] = "生成中"
                    out["content"] = data.get("data", {}).get("text", "")

                # 工作流结束
                elif event == "workflow_finished":
                    wf = data.get("data", {})
                    out["stage"] = "工作流结束"
                    out["status"] = wf.get("status")
                    out["outputs"] = wf.get("outputs")
                    if wf.get("error"):
                        out["error"] = wf.get("error")

                else:
                    out["raw"] = data

                yield f"data: {json.dumps(out, ensure_ascii=False)}\n\n"

        yield "data: [DONE]\n\n"

    except requests.RequestException as e:
        err = {"event": "error", "stage": "请求异常", "error": str(e)}
        yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"


def _sse_response(generator) -> StreamingResponse:
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ============ 路由 ============

@router.post("/travel/plan/stream")
async def travel_plan_stream(payload: TravelPlanRequest):
    """旅行规划入口：接收用户旅行参数，组装 inputs 后调用 Dify 工作流，返回 SSE 流式响应。

    请求体示例：
    {
        "destination": "昆明",
        "departure": "-",
        "days": 2,
        "people": "2",
        "budget": "3000",
        "style": "休闲",
        "special_request": "帮我安排完整行程",
        "start_date": "2026-09-11"
    }
    """
    return _sse_response(
        stream_dify_workflow(payload.to_dify_inputs(), user=payload.user)
    )


@router.post("/workflow/stream")
async def workflow_stream(payload: WorkflowRequest):
    """原始透传模式：前端通过 POST 调用，返回 SSE 流式响应。"""
    return _sse_response(
        stream_dify_workflow(payload.inputs, user=payload.user)
    )
