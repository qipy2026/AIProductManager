# 5 分钟 Demo 录屏助手
# 自动录屏（推荐）: .\scripts\record_demo.ps1 -Auto
# 手动分步（OBS/Win+G）: .\scripts\record_demo.ps1

param(
    [switch]$Auto
)

if ($Auto) {
    & (Join-Path $PSScriptRoot "record_demo_video.ps1") -SkipServer
    exit $LASTEXITCODE
}

$Base = if ($env:DEMO_BASE_URL) { $env:DEMO_BASE_URL } else { "http://localhost:3000" }

$steps = @(
    @{ Url = "$Base/chat"; Narration = "【1/9】对话页：展示导航与 Trace" },
    @{ Url = "$Base/chat"; Narration = "【2/9】输入：企业版和专业版区别？ → RAG 来源引用" },
    @{ Url = "$Base/chat"; Narration = "【3/9】输入：服务器宕机请处理 → 工单号 T-xxx" },
    @{ Url = "$Base/chat"; Narration = "【4/9】输入：查 T-001 进度 → 只查单不建单" },
    @{ Url = "$Base/chat"; Narration = "【5/9】输入：太差了要投诉 → 转人工" },
    @{ Url = "$Base/tickets"; Narration = "【6/9】工单中心：与对话分离" },
    @{ Url = "$Base/roi"; Narration = "【7/9】业务 ROI 看板 · 基线 vs 当前" },
    @{ Url = "$Base/ops"; Narration = "【8/9】运营后台 → Bad Case 七层" },
    @{ Url = "$Base/eval"; Narration = "【9/9】评测报告 → 运行全量 120 条门禁" }
)

Write-Host ""
Write-Host "=== 智服通 AgentOps · 5 分钟录屏助手 ===" -ForegroundColor Cyan
Write-Host "Base URL: $Base"
Write-Host "录屏完成后保存为: assets/demo.mp4"
Write-Host "详细分镜: scripts/record_demo.md"
Write-Host ""

foreach ($step in $steps) {
    Write-Host $step.Narration -ForegroundColor Green
    Write-Host "  -> $($step.Url)" -ForegroundColor DarkGray
    Start-Process $step.Url
    Read-Host "按 Enter 继续下一步"
}

Write-Host ""
Write-Host "演示路径完成。请停止录屏并保存为 assets/demo.mp4" -ForegroundColor Cyan
