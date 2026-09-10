# dify.py
import json
import requests
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any

# ============ 配置 ============
DIFY_API_BASE = "https://api.dify.ai/v1"   # 自建实例改成自己的地址
DIFY_API_KEY = "app-xxxxxxxxxxxxxxxx"      # Dify 应用 API Key

router = APIRouter()


class WorkflowRequest(BaseModel):
    inputs: Dict[str, Any] = {}
    query: str = ""
    user: str = "default-user"


def stream_dify_workflow(payload: WorkflowRequest):
    """调用 Dify 工作流 streaming 接口，逐条 yield SSE 数据。"""
    url = f"{DIFY_API_BASE}/workflows/run"
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "inputs": payload.inputs,
        "response_mode": "streaming",
        "user": payload.user,
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


@router.post("/workflow/stream")
async def workflow_stream(payload: WorkflowRequest):
    """前端通过 POST 调用，返回 SSE 流式响应。"""
    return StreamingResponse(
        stream_dify_workflow(payload),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )