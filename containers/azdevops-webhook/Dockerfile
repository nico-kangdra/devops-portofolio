FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl gnupg lsb-release ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash
RUN az extension add --name azure-devops
RUN az config set extension.use_dynamic_install=yes_without_prompt && \
    az config set core.output=json

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir fastapi uvicorn python-dotenv
EXPOSE 3000
CMD ["python3", "main.py"]