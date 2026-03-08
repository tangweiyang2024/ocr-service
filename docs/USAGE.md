# 使用文档

## 一、HTTP API

### 健康检查
```bash
curl http://api.cstwy.top/health
```

### OCR 识别
```bash
curl -X POST "http://api.cstwy.top/api/recognize" \
  -F "file=@test2.png" \
  -F "lang=chi_sim+eng" \
  -F "preprocess=true" \
  -F "psm=6"
```

## 二、网页前端
- 地址：`http://api.cstwy.top/`
- 功能：上传图片 -> 识别 -> 展示文本/行数/耗时

## 三、MCP 调用
MCP URL：`http://api.cstwy.top/mcp`

可用工具：
- `ocr_health`
- `ocr_recognize_file`
- `ocr_recognize_base64`

推荐调用策略：
1. 先 `ocr_health`
2. 远端可见路径用 `ocr_recognize_file`
3. 客户端本地图片用 `ocr_recognize_base64`

## 四、Codex/Claude 短提示用法

### Codex
- `识别 D:\study\ocr-service\test2.png 图片`
- `ocr test2.png 图片`

### Claude
- `/ocr test2.png`

说明：实际是否走 file/base64 由 skill 内部流程决定。