# 部署文档（物理机，无 Docker）

## 1. 目录与依赖
以 `/opt/ocr-service` 为例。

```bash
cd /opt
git clone <your_repo_url> ocr-service
cd ocr-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 -m venv .venv-mcp
source .venv-mcp/bin/activate
pip install -r requirements-mcp.txt
```

确保系统安装：
- `tesseract-ocr`
- 语言包（`chi_sim`, `eng`）
- `nginx`

## 2. OCR API systemd
复制并启用：

```bash
cp deploy/ocr-api.service /etc/systemd/system/ocr-api.service
systemctl daemon-reload
systemctl enable --now ocr-api
systemctl status ocr-api --no-pager
```

## 3. MCP systemd
复制并启用：

```bash
cp deploy/ocr-mcp.service /etc/systemd/system/ocr-mcp.service
systemctl daemon-reload
systemctl enable --now ocr-mcp
systemctl status ocr-mcp --no-pager
```

## 4. Nginx
复制配置并重载：

```bash
cp deploy/api.cstwy.top.conf /etc/nginx/conf.d/api.cstwy.top.conf
nginx -t
systemctl reload nginx
```

关键路由：
- `/` -> `127.0.0.1:18000`
- `/mcp` -> `127.0.0.1:19000/mcp`

## 5. 验证

```bash
curl http://api.cstwy.top/health
curl http://api.cstwy.top/mcp -I
curl -X POST "http://api.cstwy.top/api/recognize" -F "file=@test2.png" -F "lang=chi_sim+eng"
```

## 6. 常见问题
- `file not found on MCP server filesystem`：传的是客户端本地路径，改用 base64 工具。
- `invalid image`：图片损坏或 base64 截断。
- CPU/IO 高：保持单 worker、限制并发，避免超大图。