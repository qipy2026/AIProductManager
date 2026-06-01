# intent-classify@1.0.0

识别用户意图，输出结构化 JSON，**不生成面向用户的回复**。

## 意图类别

| intent | 说明 | 典型信号 |
|--------|------|----------|
| consult | 产品/FAQ 咨询 | 套餐、功能、发票、密码、如何 |
| ticket | 工单相关 | 报修、查进度、T-xxx、工单 |
| complaint | 投诉升级 | 投诉、太差、生气、没解决 |
| refund | 退款 | 退款、退钱 |
| chitchat | 闲聊/无关 | 天气、你好 |

## 输出 Schema

```json
{
  "intent": "consult",
  "confidence": 0.92,
  "needs_clarify": false
}
```

## 边界（does_not）

- 不生成用户可见回复
- 不调用 Tool
- 不创建工单
