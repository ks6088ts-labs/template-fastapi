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

### Microsoft Graph Sites Service

Microsoft Graph Sites サービスは、SharePoint Online のファイルを操作するためのサービスです。

```shell
# Help
uv run python scripts/msgraphs/sites.py --help

# List files in SharePoint site (site_id is required)
uv run python scripts/msgraphs/sites.py list-files <SITE_ID>

# List files in specific folder
uv run python scripts/msgraphs/sites.py list-files <SITE_ID> --folder "Documents"

# List files in JSON format
uv run python scripts/msgraphs/sites.py list-files <SITE_ID> --format json

# Upload a single file
uv run python scripts/msgraphs/sites.py upload-file <SITE_ID> "local_file.txt"

# Upload file to specific folder
uv run python scripts/msgraphs/sites.py upload-file <SITE_ID> "local_file.txt" --folder "Documents"

# Upload multiple files
uv run python scripts/msgraphs/sites.py upload-files <SITE_ID> "file1.txt" "file2.txt" "file3.txt"

# Upload multiple files to specific folder
uv run python scripts/msgraphs/sites.py upload-files <SITE_ID> "file1.txt" "file2.txt" --folder "Documents"

# Download a file
uv run python scripts/msgraphs/sites.py download-file <SITE_ID> "remote_file.txt"

# Download file from specific folder
uv run python scripts/msgraphs/sites.py download-file <SITE_ID> "remote_file.txt" --folder "Documents"

# Download file with custom output path
uv run python scripts/msgraphs/sites.py download-file <SITE_ID> "remote_file.txt" --output "downloaded_file.txt"

# Get file information
uv run python scripts/msgraphs/sites.py get-file-info <SITE_ID> "remote_file.txt"

# Get file information from specific folder
uv run python scripts/msgraphs/sites.py get-file-info <SITE_ID> "remote_file.txt" --folder "Documents"

# Delete a file
uv run python scripts/msgraphs/sites.py delete-file <SITE_ID> "remote_file.txt"

# Delete file from specific folder
uv run python scripts/msgraphs/sites.py delete-file <SITE_ID> "remote_file.txt" --folder "Documents"

# Delete file without confirmation
uv run python scripts/msgraphs/sites.py delete-file <SITE_ID> "remote_file.txt" --force

# Delete multiple files
uv run python scripts/msgraphs/sites.py delete-files <SITE_ID> "file1.txt" "file2.txt" "file3.txt"

# Delete multiple files from specific folder
uv run python scripts/msgraphs/sites.py delete-files <SITE_ID> "file1.txt" "file2.txt" --folder "Documents"

# Delete multiple files without confirmation
uv run python scripts/msgraphs/sites.py delete-files <SITE_ID> "file1.txt" "file2.txt" --force
```
