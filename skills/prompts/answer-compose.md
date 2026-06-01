# answer-compose@1.0.0

基于检索到的 chunks 组装用户可见回复，并标注来源引用。

## 输入

- `chunks` / `sources`

## 输出

- `response`：带 `[1]` 引用与 📎 来源行的回复
- 无命中时返回「抱歉，知识库中未找到…」

## 边界

- 不自行检索（依赖 knowledge-retrieve）
- 不创建工单
