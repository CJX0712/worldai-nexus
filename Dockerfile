FROM python:3.13-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# 核心依赖: requirements.txt 为最小闭包; numpy 是默认 CMD (api.main) 运行期必需,
# 一并装入以保证镜像开箱即用 (requirements-ai.txt 的语义检索 / 本地模型后端仍按需扩展)。
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt numpy==2.5.3

COPY . .

EXPOSE 8000
CMD ["python", "-m", "api.main"]
