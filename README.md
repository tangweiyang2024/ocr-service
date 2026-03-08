# OCR Service (FastAPI + Tesseract + MCP)

一个支持 HTTP API、Web 页面和 MCP 协议的 OCR 服务。

线上地址：
- 前端页面：`http://api.cstwy.top/`
- API：`http://api.cstwy.top/api/recognize`
- MCP：`http://api.cstwy.top/mcp`

## 功能
- `GET /`：OCR 前端页面
- `GET /health`：健康检查
- `POST /api/recognize`：上传图片识别（兼容 `/ocr/recognize`）
- MCP 工具：`ocr_health`、`ocr_recognize_file`、`ocr_recognize_base64`

默认准确率优先参数：
- `lang=chi_sim+eng`
- `preprocess=true`
- `psm=6`

## 快速开始

### 1) 本地运行 HTTP API
```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 2) 本地运行 MCP（stdio）
```bash
pip install -r requirements-mcp.txt
python app/mcp_server.py
```

### 3) API 调用示例
```bash
curl -X POST "http://api.cstwy.top/api/recognize" \
  -F "file=@test2.png" \
  -F "lang=chi_sim+eng" \
  -F "preprocess=true" \
  -F "psm=6"
```

## 文档目录
- 架构：[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- 使用：[`docs/USAGE.md`](docs/USAGE.md)
- 部署（物理机）：[`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)
- Skills 说明：[`docs/SKILLS.md`](docs/SKILLS.md)
- Claude OCR skill 原文：[`docs/skills/claude-ocr-skill.md`](docs/skills/claude-ocr-skill.md)
- Codex OCR skill 原文：[`docs/skills/codex-ocr-skill.md`](docs/skills/codex-ocr-skill.md)

## 部署文件
- Nginx：`deploy/api.cstwy.top.conf`
- OCR API systemd：`deploy/ocr-api.service`
- OCR MCP systemd：`deploy/ocr-mcp.service`
- Docker Compose（可选）：`deploy/docker-compose.yml`

## 关键环境变量
- `OCR_API_BASE`：MCP 转调 API 地址（默认 `http://api.cstwy.top`）
- `OCR_MCP_NAME`：MCP 服务名（默认 `ocr-service`）
- `OCR_MCP_TRANSPORT`：`stdio` 或 `streamable-http`
- `OCR_MCP_HOST`：MCP 监听地址（默认 `127.0.0.1`）
- `OCR_MCP_PORT`：MCP 端口（默认 `19000`）
- `OCR_MCP_PATH`：MCP 路径（默认 `/mcp`）
- `OCR_MAX_UPLOAD_BYTES`：上传大小限制（默认 8MB）

## 注意事项
- 客户端本地图片路径通常对远端 MCP 不可见，优先走 `ocr_recognize_base64`。
- 请勿上传敏感图片到公网服务。