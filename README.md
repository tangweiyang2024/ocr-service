# OCR API (FastAPI + Tesseract)

一个可部署到远端服务器的 OCR 识别服务，提供 HTTP 接口和网页界面。

## 功能

- `GET /`：OCR 网页界面
- `GET /health`：健康检查
- `POST /api/recognize`：图片 OCR 识别（兼容 `POST /ocr/recognize`）
- 支持中英文识别（默认 `chi_sim+eng`）
- 支持简单图像预处理（灰度、锐化、对比度增强）

## 接口说明

### 1) 健康检查

```bash
curl http://<SERVER_IP>:8000/health
```

示例返回：

```json
{"status":"ok"}
```

### 2) OCR 识别

请求：`multipart/form-data`

- `file`：图片文件（必填）
- `lang`：OCR 语言（可选，默认 `chi_sim+eng`）
- `preprocess`：是否预处理（可选，默认 `true`）

```bash
curl -X POST "http://<SERVER_IP>:8000/api/recognize" \
  -F "file=@./demo.png" \
  -F "lang=chi_sim+eng" \
  -F "preprocess=true"
```

示例返回：

```json
{
  "filename": "demo.png",
  "lang": "chi_sim+eng",
  "text": "识别出的全文...",
  "lines": ["第1行", "第2行"],
  "line_count": 2
}
```

## 本地运行

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

> 注意：本地非 Docker 运行时，需要先安装 Tesseract 引擎及语言包。

## Docker 运行（推荐）

### 方式一：Docker

```bash
docker build -t ocr-api:latest .
docker run -d --name ocr-api -p 127.0.0.1:18000:8000 --restart unless-stopped ocr-api:latest
```

### 方式二：Docker Compose

```bash
docker compose -f deploy/docker-compose.yml up -d --build
```

## 远端服务器部署步骤（Ubuntu 示例）

1. 安装 Docker / Docker Compose
2. 上传代码到服务器（`git clone` 或 `scp`）
3. 进入项目目录执行：

```bash
docker compose -f deploy/docker-compose.yml up -d --build
```

4. Nginx 反向代理 `127.0.0.1:18000`，建议路径前缀 `/ocr/`
5. 访问 `https://<DOMAIN>/ocr/` 使用网页，`https://<DOMAIN>/ocr/docs` 查看 Swagger

## 生产建议

- 在前面加 Nginx 反向代理，并启用 HTTPS
- 增加接口鉴权（API Key / JWT）
- 限制上传大小与并发，防止滥用
- 记录请求日志和错误日志
