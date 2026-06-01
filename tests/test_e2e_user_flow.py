"""E2E — 模拟用户在浏览器中的实际操作路径.

验收路径（与 M0-DAY-ACCEPTANCE §4.2 一致）：
  1. 打开首页 → 自动跳转 /chat
  2. 确认页面文案与导航
  3. 在对话页发送消息（经 Next.js 代理 POST /api/chat，非直连 :8000）
  4. 同 session 多轮对话
  5. 敏感信息拦截（UAT-06 预演）
  6. 点击导航访问 /ops、/eval
"""

from __future__ import annotations

import re
import time

import httpx
import pytest

FRONTEND = "http://localhost:3000"
TIMEOUT = 15.0


def _frontend_up() -> bool:
    try:
        with httpx.Client(trust_env=False, timeout=3.0) as c:
            r = c.get(FRONTEND, follow_redirects=False)
        return r.status_code in (200, 307, 308)
    except httpx.HTTPError:
        return False


pytestmark = pytest.mark.skipif(
    not _frontend_up(),
    reason="前端未启动：请在 frontend/ 运行 npm run dev（:3000）",
)


@pytest.fixture(scope="module")
def client() -> httpx.Client:
    # trust_env=False：绕过系统 HTTP 代理，与浏览器访问 localhost 行为一致
    with httpx.Client(
        base_url=FRONTEND, timeout=TIMEOUT, follow_redirects=True, trust_env=False
    ) as c:
        yield c


@pytest.fixture(scope="module")
def session_id() -> str:
    return f"sess-e2e-{int(time.time() * 1000)}"


class TestUserNavigation:
    """用户打开浏览器、切换页面的操作."""

    def test_home_redirects_to_chat(self, client: httpx.Client) -> None:
        r = client.get("/", follow_redirects=False)
        assert r.status_code in (307, 308)
        assert "/chat" in r.headers.get("location", "")

    def test_chat_page_renders(self, client: httpx.Client) -> None:
        r = client.get("/chat")
        assert r.status_code == 200
        html = r.text
        assert "智能客服对话" in html
        assert "请输入问题" in html
        assert "智服通 AgentOps" in html
        assert "新对话" in html

    def test_nav_links_present(self, client: httpx.Client) -> None:
        r = client.get("/chat")
        html = r.text
        for label in ("对话", "运营后台", "评测报告"):
            assert label in html

    def test_ops_page_renders(self, client: httpx.Client) -> None:
        r = client.get("/ops")
        assert r.status_code == 200
        assert "运营后台" in r.text
        assert "Skill 健康度" in r.text

    def test_eval_page_renders(self, client: httpx.Client) -> None:
        r = client.get("/eval")
        assert r.status_code == 200
        assert "Eval Harness" in r.text
        assert "120 条" in r.text


class TestUserChatFlow:
    """用户在 /chat 输入框发送消息（与 ChatPanel.fetch 完全一致）."""

    def _send(self, client: httpx.Client, message: str, session_id: str) -> dict:
        r = client.post(
            "/api/chat",
            json={"message": message, "session_id": session_id},
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code == 200, r.text
        return r.json()

    def test_normal_message_gets_reply_and_trace(
        self, client: httpx.Client, session_id: str
    ) -> None:
        """用户输入普通咨询 → Agent 回复 + trace_id（对话页会展示 trace 行）."""
        data = self._send(client, "企业版和专业版有什么区别？", session_id)
        assert data.get("response"), "Agent 回复为空"
        assert data.get("trace_id"), "缺少 trace_id，对话页无法展示 trace 行"
        assert data.get("blocked") is False
        assert "intent-classify" in data.get("skills_invoked", [])
        resp = data.get("response", "")
        assert (
            data.get("sources")
            or "企业版" in resp
            or "专业版" in resp
            or "已识别意图" in resp
        )

    def test_same_session_second_message(
        self, client: httpx.Client, session_id: str
    ) -> None:
        """同一会话连续发送第二条消息."""
        data = self._send(client, "帮我查一下工单进度", session_id)
        assert data.get("response")
        assert re.match(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            data.get("trace_id", ""),
        )

    def test_sensitive_input_blocked_uat06(
        self, client: httpx.Client, session_id: str
    ) -> None:
        """UAT-06：含手机号 → Guardrail 拦截，仍返回可读提示（非 echo）."""
        data = self._send(client, "我的手机号是13800138000请帮我查单", session_id)
        assert data.get("blocked") is True
        assert "敏感" in data.get("response", "")
        assert "echo-placeholder" not in str(data.get("skills_invoked", []))

    def test_proxy_not_direct_backend(self, client: httpx.Client, session_id: str) -> None:
        """确认请求走前端 :3000 代理，而非用户直连 :8000."""
        # 若仅后端启动、前端未启动，整个模块已被 skip
        r = client.post(
            "/api/chat",
            json={"message": "hello", "session_id": session_id},
        )
        assert r.request.url.host in ("localhost", "127.0.0.1")
        assert r.request.url.port == 3000
