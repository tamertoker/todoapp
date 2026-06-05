import json
import os
import re

base_path = 'src/leveltodo/infrastructure/persistence/sqlite/migrations/versions/'
files = os.listdir(base_path)
files = [f for f in files if f.endswith('.py')]

rev_to_file = {}
for f in files:
    path = base_path + f
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
        rev = re.search(r'revision: str = "(.*?)"', content)
        if rev:
            rev_to_file[rev.group(1)] = f"file:{path}"

with open('.understand-anything/intermediate/batch-12.json', 'r', encoding='utf-8') as f:
    batch = json.load(f)

for f in files:
    path = base_path + f
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
        down_rev = re.search(r'down_revision: str \| None = "(.*?)"', content)
        if down_rev:
            target_rev = down_rev.group(1)
            if target_rev in rev_to_file:
                batch['edges'].append({
                    'source': f"file:{path}",
                    'target': rev_to_file[target_rev],
                    'type': 'depends_on'
                })

with open('.understand-anything/intermediate/batch-12.json', 'w', encoding='utf-8') as f:
    json.dump(batch, f, indent=2, ensure_ascii=False)
