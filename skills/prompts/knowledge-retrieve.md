# knowledge-retrieve@1.0.0

从 Semantic Memory / FAQ 检索与用户问题相关的知识片段。

## 输入

- `message`：用户原话
- `semantic_hits`（可选）：Router 预检索结果

## 输出

- `chunks`：命中文档列表
- `sources`：来源元数据（id, title, url）
- `require_source`: true

## 边界

- 不生成面向用户的最终回复
- 不调用外部 Tool
