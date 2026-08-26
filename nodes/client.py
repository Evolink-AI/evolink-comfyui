"""EvoLink API 统一客户端：鉴权、任务提交、轮询、错误码到中文提示的映射。

接口契约（2026-08-06 按官方文档逐项核实）：
  POST https://api.evolink.ai/v1/images/generations   提交生成任务
  GET  https://api.evolink.ai/v1/tasks/{id}           查询任务
状态机 pending -> processing -> completed / failed，progress 0-100，
结果链接 24 小时过期，失败任务不扣费。
"""

import asyncio
import time

import requests

API_BASE = "https://api.evolink.ai/v1"
FILES_API_BASE = "https://files-api.evolink.ai/api/v1"
USER_AGENT = "comfyui-evolink/1.0.0"

# HTTP 状态码 -> 给用户看的中文提示
HTTP_HINTS = {
    400: "请求参数无效，请检查 prompt/size 等填写 (invalid_request)",
    401: "API Key 无效或已删除，请到 https://evolink.ai/dashboard/keys 核对或重建 (unauthorized)",
    402: "账户余额不足，请到 https://evolink.ai 充值后重试 (insufficient_quota)",
    403: "当前账户无权访问该模型 (model_access_denied)",
    429: "请求过于频繁，请稍等片刻再运行 (rate_limit_exceeded)",
}

# 任务 failed 时 error.code -> 中文提示
TASK_ERROR_HINTS = {
    "content_policy_violation": "提示词或参考图触发内容审核，请调整后重试（失败任务不扣费）",
    "internal_error": "服务端内部错误，请稍后重试（失败任务不扣费）",
    "timeout": "任务超时（失败任务不扣费）",
}


class EvoLinkError(RuntimeError):
    """带中文提示的 API 错误。"""


def _headers(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }


def _error_from_response(resp):
    detail = ""
    try:
        body = resp.json()
        err = body.get("error") or {}
        detail = err.get("message") or body.get("msg") or ""
    except ValueError:
        detail = (resp.text or "")[:200]
    hint = HTTP_HINTS.get(resp.status_code, "")
    parts = [f"EvoLink API 错误 HTTP {resp.status_code}"]
    if hint:
        parts.append(hint)
    if detail:
        parts.append(f"服务端信息: {detail}")
    return EvoLinkError("；".join(parts))


def request_json(method, url, api_key, payload=None, timeout=60):
    """发请求并解析 JSON。网络错误 / 5xx 自动重试 1 次，其余直接抛错。"""
    last_exc = None
    for attempt in range(2):
        try:
            resp = requests.request(
                method, url, headers=_headers(api_key), json=payload, timeout=timeout
            )
        except requests.RequestException as e:
            last_exc = EvoLinkError(
                f"网络请求失败：{e}。请检查网络/代理设置（若使用 VPN，"
                "请将 api.evolink.ai 与 files-api.evolink.ai 加入直连规则）。"
            )
            time.sleep(2)
            continue
        if resp.status_code >= 500:
            last_exc = _error_from_response(resp)
            time.sleep(2)
            continue
        if resp.status_code >= 400:
            raise _error_from_response(resp)
        try:
            return resp.json()
        except ValueError:
            raise EvoLinkError(f"服务端返回了无法解析的内容：{(resp.text or '')[:200]}")
    raise last_exc


def submit_task(api_key, path, payload):
    """提交异步生成任务（图像/视频通用），返回任务对象（含 id/status/usage.credits_reserved）。

    path 形如 "/images/generations"、"/videos/generations"。
    """
    task = request_json("POST", f"{API_BASE}{path}", api_key, payload)
    if not task.get("id"):
        raise EvoLinkError(f"提交任务后未返回任务 ID，原始响应：{str(task)[:200]}")
    return task


def submit_image_task(api_key, payload):
    """提交图像生成任务，返回任务对象（含 id/status/usage.credits_reserved）。"""
    return submit_task(api_key, "/images/generations", payload)


def get_credits(api_key):
    """查询账户余额。返回 (user_remaining, token_remaining, token_unlimited)。"""
    body = request_json("GET", f"{API_BASE}/credits", api_key)
    data = body.get("data") or {}
    user = data.get("user") or {}
    token = data.get("token") or {}
    return (
        float(user.get("remaining_credits") or 0.0),
        float(token.get("remaining_credits") or 0.0),
        bool(token.get("unlimited_credits")),
    )


def get_task(api_key, task_id):
    return request_json("GET", f"{API_BASE}/tasks/{task_id}", api_key)


def _handle_task_status(info, task_id, deadline, timeout_seconds, progress_callback):
    """公共状态机：completed 返回 info，failed/超时抛错，进行中返回 None。"""
    status = info.get("status", "")
    if progress_callback is not None:
        try:
            progress_callback(int(info.get("progress") or 0))
        except Exception:
            pass
    if status == "completed":
        return info
    if status == "failed":
        err = info.get("error") or {}
        code = err.get("code", "")
        hint = TASK_ERROR_HINTS.get(
            code, f"{err.get('message', '未知错误')}（失败任务不扣费）"
        )
        raise EvoLinkError(
            f"任务失败：{hint}。任务 ID: {task_id}，"
            "可到 https://evolink.ai/zh/dashboard/logs 查看详情。"
        )
    if time.monotonic() > deadline:
        raise EvoLinkError(
            f"等待超时（{timeout_seconds}s）。任务可能仍在后台运行，"
            f"任务 ID: {task_id}，可到 https://evolink.ai/zh/dashboard/logs "
            "查看最终状态与扣费（超时失败的任务不会扣费）。"
        )
    return None


def poll_task(api_key, task_id, timeout_seconds=300, progress_callback=None):
    """同步轮询任务直到 completed/failed/超时。间隔 3s 起指数退避，上限 10s。"""
    interval = 3.0
    deadline = time.monotonic() + timeout_seconds
    while True:
        time.sleep(interval)
        interval = min(interval * 1.5, 10.0)
        info = get_task(api_key, task_id)
        done = _handle_task_status(info, task_id, deadline, timeout_seconds, progress_callback)
        if done is not None:
            return done


def _interrupt_check():
    """ComfyUI 里用户点「取消」时抛 InterruptProcessingException；单测环境静默。"""
    try:
        from comfy import model_management
    except Exception:
        return
    model_management.throw_exception_if_processing_interrupted()


async def poll_task_async(api_key, task_id, timeout_seconds=300,
                          progress_callback=None, max_interval=10.0):
    """异步轮询：等待时让出事件循环（不阻塞 ComfyUI 队列），每 0.5s 响应一次取消。

    视频任务动辄数分钟，必须用这个而不是 poll_task。
    用户取消时抛出 ComfyUI 的中断异常，并提示 task_id 供后续用
    GET /v1/tasks/{id} 取回结果（服务端任务不会因此停止，完成仍会扣费）。
    """
    interval = 3.0
    deadline = time.monotonic() + timeout_seconds
    try:
        while True:
            waited = 0.0
            while waited < interval:
                _interrupt_check()
                await asyncio.sleep(0.5)
                waited += 0.5
            interval = min(interval * 1.5, max_interval)
            info = await asyncio.to_thread(get_task, api_key, task_id)
            done = _handle_task_status(info, task_id, deadline, timeout_seconds, progress_callback)
            if done is not None:
                return done
    except EvoLinkError:
        raise
    except Exception as e:
        if type(e).__name__ == "InterruptProcessingException":
            print(f"[EvoLink] 已取消等待。任务 {task_id} 仍在服务端运行，"
                  "完成后可到 https://evolink.ai/zh/dashboard/logs 查看结果与扣费。")
        raise
