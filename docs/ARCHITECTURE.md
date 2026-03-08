# 项目架构

## 总览
该项目提供两条能力链路：

1. HTTP OCR API（FastAPI）
2. MCP OCR Server（对外暴露 MCP 工具，内部转调 HTTP OCR API）

```text
[Client/Web]
   | HTTP
   v
[Nginx api.cstwy.top]
   |-- /            -> 127.0.0.1:18000 (FastAPI OCR)
   |-- /api/*       -> 127.0.0.1:18000 (FastAPI OCR)
   |-- /health      -> 127.0.0.1:18000
   |-- /mcp         -> 127.0.0.1:19000/mcp (MCP Server)

[MCP Client (Codex/Claude/Script)]
   | MCP streamable-http
   v
[ocr-service MCP]
   | HTTP multipart/base64
   v
[OCR API /api/recognize]
   | Tesseract + 预处理
   v
[JSON 识别结果]
```

## 目录结构
- `app/main.py`: OCR API（`/`, `/health`, `/api/recognize`）
- `app/mcp_server.py`: MCP server，工具：
  - `ocr_health`
  - `ocr_recognize_file`
  - `ocr_recognize_base64`
- `web/`: 前端页面资源
- `deploy/api.cstwy.top.conf`: Nginx 反向代理配置
- `deploy/ocr-api.service`: OCR API systemd 服务
- `deploy/ocr-mcp.service`: MCP systemd 服务
- `docs/skills/`: Claude/Codex OCR skill 原文归档

## 关键设计
- 准确率优先默认参数：`lang=chi_sim+eng`, `preprocess=true`, `psm=6`
- 资源保护：限制上传大小、并发、超时、线程数
- 本地路径不可达处理：客户端本地文件优先使用 base64 上传到 MCP