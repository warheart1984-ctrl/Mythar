FROM python:3.12-slim
WORKDIR /app
COPY mythar-v0.2 /app/mythar-v0.2
COPY mythar-registry/registry-v0.1.json /app/mythar-registry/registry-v0.1.json
COPY mythar-registry/registry-v0.2.json /app/mythar-registry/registry-v0.2.json
COPY mythar-registry/registry-v0.3.json /app/mythar-registry/registry-v0.3.json
ENV PYTHONPATH=/app/mythar-v0.2/src
ENV MYTHAR_REGISTRY_DIR=/app/mythar-registry
EXPOSE 8080
CMD ["python", "-m", "mythar", "serve", "--host", "0.0.0.0", "--port", "8080"]
