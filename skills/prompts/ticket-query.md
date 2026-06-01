# ticket-query@1.0.0

查询工单状态与进度。

## 输入

- `message` 中的 `T-xxx` 或 Episodic 中的历史工单号

## 输出

- `response`：状态、标题
- `ticket_id`

## Fallback

- 无工单号 → 引导用户提供

## 边界

- 不创建新工单
