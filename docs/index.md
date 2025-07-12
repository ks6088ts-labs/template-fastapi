# template-fastapi

## Get started

```shell
# Install dependencies
make install-deps-dev

# Set up credentials
cp .env.example .env
# Edit .env to set your credentials
```

### Foodies Service

```shell
# Help
uv run python scripts/foodies_restaurants.py --help

# Import mock data
uv run python scripts/foodies_restaurants.py import-data --csv-file ./datasets/foodies_restaurants.csv

# Search restaurants
uv run python scripts/foodies_restaurants.py search --query "sushi"

# Find nearby restaurants
uv run python scripts/foodies_restaurants.py find-nearby --latitude 35.681167 --longitude 139.767052 --distance 5.0

# Run FastAPI server in development mode
make dev
```

### Files Service

```shell
# Help
uv run python scripts/files.py --help

# List all files
uv run python scripts/files.py list-files

# List files with prefix
uv run python scripts/files.py list-files --prefix "images/"

# Upload a single file
uv run python scripts/files.py upload-file ./path/to/file.txt

# Upload a single file with custom blob name
uv run python scripts/files.py upload-file ./path/to/file.txt --name "custom-name.txt"

# Upload multiple files
uv run python scripts/files.py upload-multiple-files ./file1.txt ./file2.jpg ./file3.pdf

# Download a file
uv run python scripts/files.py download-file "file.txt"

# Download a file to specific location
uv run python scripts/files.py download-file "file.txt" --output "./downloads/file.txt"

# Get file information
uv run python scripts/files.py get-file-info "file.txt"

# Delete a file (with confirmation)
uv run python scripts/files.py delete-file "file.txt"

# Delete a file (without confirmation)
uv run python scripts/files.py delete-file "file.txt" --force

# Delete multiple files
uv run python scripts/files.py delete-multiple-files "file1.txt" "file2.jpg" "file3.pdf"

# Delete multiple files (without confirmation)
uv run python scripts/files.py delete-multiple-files "file1.txt" "file2.jpg" "file3.pdf" --force
```

### Speeches Service

```shell
AZURE_BLOB_STORAGE_CONTAINER_SAS_TOKEN="<your_sas_token>"
AZURE_BLOB_STORAGE_CONTAINER_URL="https://<storage_account_name>.blob.core.windows.net/<container_name>"
FILE_NAME="path/to/your/audio/file.wav"
URL="${AZURE_BLOB_STORAGE_CONTAINER_URL}/${FILE_NAME}?${AZURE_BLOB_STORAGE_CONTAINER_SAS_TOKEN}"

# Help
uv run python scripts/speeches.py --help

# Create a new transcription job
uv run python scripts/speeches.py create-transcription "$URL" \
  --locale "ja-JP" \
  --name "My Transcription"

# Get transcription job status
uv run python scripts/speeches.py get-transcription "$JOB_ID"

# Wait for transcription completion
uv run python scripts/speeches.py wait-for-completion "$JOB_ID" --timeout 300 --interval 10

# Get transcription files
uv run python scripts/speeches.py get-transcription-files "$JOB_ID"

# Get transcription result
uv run python scripts/speeches.py get-transcription-result "https://<contentUrl>" --save "result.json"

# List all transcription jobs
uv run python scripts/speeches.py list-transcriptions

# Delete transcription job
uv run python scripts/speeches.py delete-transcription "$JOB_ID"

# Delete transcription job (without confirmation)
uv run python scripts/speeches.py delete-transcription "$JOB_ID" --force
```

## Microsoft Graph API

- [Build Python apps with Microsoft Graph](https://learn.microsoft.com/en-us/graph/tutorials/python?tabs=aad)

### Fundamentals

```shell
# Help
uv run python scripts/microsoft_graphs.py --help

# Get access token
uv run python scripts/microsoft_graphs.py get-access-token

# Get my profile
uv run python scripts/microsoft_graphs.py get-my-profile \
  --access-token $ACCESS_TOKEN \
  --expires-on $EXPIRES_ON

# Get SharePoint sites
uv run python scripts/microsoft_graphs.py get-sites \
  --site-id $SITE_ID \
  --access-token $ACCESS_TOKEN \
  --expires-on $EXPIRES_ON
```

## MCP

- [FastAPI-MCP](https://github.com/tadata-org/fastapi_mcp)
- [FastAPI で作成した API エンドポイントをモデル コンテキスト プロトコル (MCP) ツールとして公開してみる](https://dev.classmethod.jp/articles/fastapi-api-mcp/)
- [MCP Inspector > docs](https://modelcontextprotocol.io/docs/tools/inspector)
- [MCP Inspector > codes](https://github.com/modelcontextprotocol/inspector)

## FastAPI

- [FastAPI](https://fastapi.tiangolo.com/)
- [Settings and Environment Variables](https://fastapi.tiangolo.com/advanced/settings/)
- [WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)

## OpenTelemetry

- [Docs > Language APIs & SDKs > Python > Getting Started](https://opentelemetry.io/docs/languages/python/getting-started/)

## Azure

### Azure Functions

- [Azure Functions で OpenTelemetry を使用する](https://learn.microsoft.com/ja-jp/azure/azure-functions/opentelemetry-howto?tabs=app-insights&pivots=programming-language-python)
- [Using FastAPI Framework with Azure Functions](https://learn.microsoft.com/en-us/samples/azure-samples/fastapi-on-azure-functions/fastapi-on-azure-functions/)
- [ks6088ts-labs/azure-functions-python](https://github.com/ks6088ts-labs/azure-functions-python)

### Azure Cosmos DB

- [VectorDistance() を使用したクエリによるベクトル検索を実行する](https://learn.microsoft.com/ja-jp/azure/cosmos-db/nosql/vector-search#perform-vector-search-with-queries-using-vectordistance)
- [Azure Cosmos DB for NoSQL での改ページ](https://learn.microsoft.com/ja-jp/azure/cosmos-db/nosql/query/pagination)
- [OFFSET LIMIT (NoSQL クエリ)](https://learn.microsoft.com/ja-jp/azure/cosmos-db/nosql/query/offset-limit)
- [LangChain / Azure Cosmos DB No SQL](https://python.langchain.com/docs/integrations/vectorstores/azure_cosmos_db_no_sql/)

```shell
# Azure Cosmos DB のローカル認証を有効にする
# (注意: この操作はセキュリティ上のリスクを伴うため、開発環境でのみ使用してください。)
az resource update \
  --resource-group $RESOURCE_GROUP \
  --name $COSMOS_DB_ACCOUNT_NAME \
  --resource-type "Microsoft.DocumentDB/databaseAccounts" \
  --set properties.disableLocalAuth=false
```

### Azure Blob Storage

- [クイック スタート: Python 用 Azure Blob Storage クライアント ライブラリ](https://learn.microsoft.com/ja-jp/azure/storage/blobs/storage-quickstart-blobs-python?tabs=connection-string%2Croles-azure-portal%2Csign-in-azure-cli&pivots=blob-storage-quickstart-scratch)

### Application Insights

- [Application Insights の概要 - OpenTelemetry の可観測性](https://learn.microsoft.com/ja-jp/azure/azure-monitor/app/app-insights-overview)
- [Azure Monitor OpenTelemetry を設定する](https://learn.microsoft.com/ja-jp/azure/azure-monitor/app/opentelemetry-configuration?tabs=python)
- [open-telemetry/opentelemetry-python > Basic Trace](https://github.com/open-telemetry/opentelemetry-python/tree/main/docs/examples/basic_tracer)
- [FastAPI のテレメトリデータを Azure Application Insights に送る](https://qiita.com/hoto17296/items/2f366dfabdbe3d1d4e97)
- [【Azure Functions】 - Application Insights のログが表示されない問題](https://zenn.dev/headwaters/articles/ff19f7e1b99b44)
- [opentelemetry-instrumentation-fastapi (python) から OpenTelemetry に入門する](https://zenn.dev/taxin/articles/opentelemetry-fast-api-instrumentation-basics)

### Azure AI Speech

- [バッチ文字起こしとは](https://learn.microsoft.com/ja-jp/azure/ai-services/speech-service/batch-transcription)

### Azure AI Foundry

- [Quickstart: Create a new agent](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/quickstart?pivots=programming-language-python-azure)
- [Deep Research tool (preview)](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/quickstart?pivots=programming-language-python-azure)

#### CLI 実行例

```bash
# エージェントを作成
uv run python scripts/agents_azure_ai_foundry.py create-agent "研究アシスタント" --description "研究をサポートするAIアシスタント" --instructions "あなたは研究者をサポートするAIアシスタントです。質問に対して詳細で正確な回答を提供してください。"

# エージェント一覧を取得
uv run python scripts/agents_azure_ai_foundry.py list-agents

# エージェントの詳細を取得
uv run python scripts/agents_azure_ai_foundry.py get-agent <agent_id>

# エージェントとチャット
uv run python scripts/agents_azure_ai_foundry.py chat <agent_id> "機械学習の最新トレンドについて教えてください"

# エージェントを削除
uv run python scripts/agents_azure_ai_foundry.py delete-agent <agent_id>
```

### LangGraph Agent

LangGraph ベースのエージェント API を使用した対話型 AI アシスタント。ツール呼び出し機能を持つシンプルなエージェントワークフローを実装しています。

#### CLI 実行例

```bash
# ヘルプ
uv run python scripts/agents_langgraph.py --help

# エージェントとチャット
uv run python scripts/agents_langgraph.py chat "こんにちは！今何時ですか？"

# スレッドIDを指定してチャット（会話の継続）
uv run python scripts/agents_langgraph.py chat "前回の続きを教えてください" --thread-id "12345-67890-abcdef"

# 詳細情報付きでチャット
uv run python scripts/agents_langgraph.py chat "2 + 2 × 3 を計算してください" --verbose

# 対話モード
uv run python scripts/agents_langgraph.py interactive

# 利用可能なツール一覧
uv run python scripts/agents_langgraph.py tools

# デモモード（サンプル質問のテスト）
uv run python scripts/agents_langgraph.py demo
```

#### API エンドポイント

```bash
# FastAPIサーバーを起動
make dev

# LangGraphエージェントとチャット
curl -X POST "http://localhost:8000/agents/langgraph/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "こんにちは！"}'

# ストリーミングチャット
curl -X POST "http://localhost:8000/agents/langgraph/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"message": "長い回答をお願いします"}'

# 利用可能なツール一覧
curl -X GET "http://localhost:8000/agents/langgraph/tools"

# ヘルスチェック
curl -X GET "http://localhost:8000/agents/langgraph/health"
```
