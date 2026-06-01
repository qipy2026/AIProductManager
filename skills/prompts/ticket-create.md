# ticket-create@1.0.0

根据用户报修描述创建工单。

## 输入

- `message`：报修描述
- `profile`（可选）：VIP 影响优先级

## 输出

- `ticket_id`
- `response`：含 `T-xxx` 工单号

## Fallback

- 仅「我要报修」→ 引导补充标题/优先级模板

## 边界

- 不查询已有工单进度
