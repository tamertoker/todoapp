import json
import os

batches_file = r'C:\Users\tamer\Desktop\todoapp\todoapp\.understand-anything\intermediate\batches.json'

with open(batches_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

target_batches = [36, 37, 38, 39, 40, 41, 42]
result = {}

for batch in data['batches']:
    idx = batch['batchIndex']
    if idx in target_batches:
        result[idx] = [f['path'] for f in batch['files'] if f['path'].endswith('.py')]

print(json.dumps(result, indent=2))
