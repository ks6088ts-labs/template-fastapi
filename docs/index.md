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

## MCP

- [FastAPI-MCP](https://github.com/tadata-org/fastapi_mcp)
- [FastAPI で作成した API エンドポイントをモデル コンテキスト プロトコル (MCP) ツールとして公開してみる](https://dev.classmethod.jp/articles/fastapi-api-mcp/)
- [MCP Inspector > docs](https://modelcontextprotocol.io/docs/tools/inspector)
- [MCP Inspector > codes](https://github.com/modelcontextprotocol/inspector)

## FastAPI

- [FastAPI](https://fastapi.tiangolo.com/)
- [Settings and Environment Variables](https://fastapi.tiangolo.com/advanced/settings/)

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

### Application Insights

- [Application Insights の概要 - OpenTelemetry の可観測性](https://learn.microsoft.com/ja-jp/azure/azure-monitor/app/app-insights-overview)
- [Azure Monitor OpenTelemetry を設定する](https://learn.microsoft.com/ja-jp/azure/azure-monitor/app/opentelemetry-configuration?tabs=python)
- [open-telemetry/opentelemetry-python > Basic Trace](https://github.com/open-telemetry/opentelemetry-python/tree/main/docs/examples/basic_tracer)
- [FastAPI のテレメトリデータを Azure Application Insights に送る](https://qiita.com/hoto17296/items/2f366dfabdbe3d1d4e97)
- [【Azure Functions】 - Application Insights のログが表示されない問題](https://zenn.dev/headwaters/articles/ff19f7e1b99b44)
- [opentelemetry-instrumentation-fastapi (python) から OpenTelemetry に入門する](https://zenn.dev/taxin/articles/opentelemetry-fast-api-instrumentation-basics)
