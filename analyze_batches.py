import json

with open('.understand-anything/intermediate/batches.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for batch in data.get('batches', []):
    if batch.get('batchIndex') == 9:
        print(f"Batch 9 Files:")
        for file in batch.get('files', []):
            print(f"  {file['path']}")
