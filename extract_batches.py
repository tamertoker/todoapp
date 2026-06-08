import json

with open(".understand-anything/intermediate/batches.json", "r") as f:
    data = json.load(f)

batches_to_extract = [1, 2, 3, 4]
extracted = {}

for batch in data.get("batches", []):
    idx = batch.get("batchIndex")
    if idx in batches_to_extract:
        extracted[idx] = [f["path"] for f in batch.get("files", [])]

print(json.dumps(extracted, indent=2))
