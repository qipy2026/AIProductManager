# 演示录屏素材

将 5 分钟产品演示视频放在此目录：

```
assets/demo.mp4
```

## 如何生成

**自动录屏（推荐）**

```powershell
# 确保前后端已启动（:3000 / :8002 或 docker compose up）
.\scripts\record_demo.ps1 -Auto
# 或
.\scripts\record_demo_video.ps1 -SkipServer
```

Playwright 自动走演示动线并输出 `assets/demo.mp4`（约 1 分钟）。

**手动分步（OBS / Win+G）**

1. 启动 Demo：见 [docs/DEMO.md](../docs/DEMO.md)
2. 运行旁白提示：`.\scripts\record_demo.ps1`
3. 按 [scripts/record_demo.md](../scripts/record_demo.md) 分镜执行

## 投递

在 README 中添加录屏链接或 `assets/demo.mp4` 路径。
