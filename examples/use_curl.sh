# 1) Load dataset
curl -sS -X POST http://localhost:8000/mcp/run \
  -H 'Content-Type: application/json' \
  -d '{"tool":"load_dataset","args":{"source":"a,b\n1,2","source_type":"inline"}}'

# 2) Create suite
curl -sS -X POST http://localhost:8000/mcp/run \
  -H 'Content-Type: application/json' \
  -d '{"tool":"create_suite","args":{"suite_name":"test","dataset_handle":"<HANDLE>","profiler":false}}'
