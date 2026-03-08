# Skills 文档

本仓库保留两份 OCR skill 原文，方便对比和迁移：

- Claude 版本：`docs/skills/claude-ocr-skill.md`
- Codex 版本：`docs/skills/codex-ocr-skill.md`

## 主要区别
- Claude skill：说明更完整、教程导向。
- Codex skill：执行导向，适配短提示触发，默认准确率参数内置。

## 当前推荐（Codex）
用户只需输入短提示，例如：
- `识别 D:\study\ocr-service\test2.png 图片`

skill 内部自动：
1. `ocr_health`
2. 路径可见性判断
3. `ocr_recognize_file` 或 `ocr_recognize_base64`
4. 返回文本与统计