
import ast
import json
import os
import re

def analyze_python_content(file_path, content):
    nodes = []
    edges = []
    
    file_id = f"file:{file_path}"
    nodes.append({
        "id": file_id,
        "type": "file",
        "name": os.path.basename(file_path),
        "summary": f"{file_path} kaynak kodu dosyası.",
        "tags": ["python", "source"]
    })
    
    try:
        tree = ast.parse(content)
    except Exception:
        return nodes, edges
        
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_id = f"class:{file_path}:{node.name}"
            nodes.append({
                "id": class_id,
                "type": "class",
                "name": node.name,
                "summary": f"{node.name} sınıfı.",
                "tags": ["class"]
            })
            edges.append({
                "source": class_id,
                "target": file_id,
                "type": "defined_in"
            })
            
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    func_id = f"function:{file_path}:{node.name}.{item.name}"
                    nodes.append({
                        "id": func_id,
                        "type": "function",
                        "name": item.name,
                        "summary": f"{node.name} sınıfı içindeki {item.name} metodu.",
                        "tags": ["method"]
                    })
                    edges.append({
                        "source": func_id,
                        "target": class_id,
                        "type": "member_of"
                    })
        
        elif isinstance(node, ast.FunctionDef):
            func_id = f"function:{file_path}:{node.name}"
            nodes.append({
                "id": func_id,
                "type": "function",
                "name": node.name,
                "summary": f"{node.name} fonksiyonu.",
                "tags": ["function"]
            })
            edges.append({
                "source": func_id,
                "target": file_id,
                "type": "defined_in"
            })

    return nodes, edges

def process_batch_1():
    base_path = r'C:\Users\tamer\Desktop\todoapp\todoapp'
    output_nodes = []
    output_edges = []
    
    # Files directly in Batch 1
    batch_1_files = ['CLAUDE.md', 'DURUM.md', 'README.md', 'alembic.ini', 'pyproject.toml']
    for f in batch_1_files:
        full_path = os.path.join(base_path, f)
        if os.path.exists(full_path):
            ftype = "document" if f.endswith(".md") else "config"
            output_nodes.append({
                "id": f"file:{f}",
                "type": ftype,
                "name": f,
                "summary": f"{f} dosyası.",
                "tags": [ftype]
            })
            
    # Process tum_proje_kodlari.txt
    kodlari_path = os.path.join(base_path, 'tum_proje_kodlari.txt')
    if os.path.exists(kodlari_path):
        with open(kodlari_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Split by file separators
        file_blocks = re.split(r'--- START OF FILE: (.*?) ---', content)
        for i in range(1, len(file_blocks), 2):
            rel_path = file_blocks[i].strip()
            # Find the end of this file's block
            end_marker = f'--- END OF FILE: {rel_path} ---'
            file_content = file_blocks[i+1].split(end_marker)[0].strip()
            
            if rel_path.endswith('.py'):
                n, e = analyze_python_content(rel_path, file_content)
                output_nodes.extend(n)
                output_edges.extend(e)
            else:
                ftype = "document" if rel_path.endswith(".md") else ("config" if rel_path.endswith((".ini", ".toml")) else "file")
                output_nodes.append({
                    "id": f"file:{rel_path}",
                    "type": ftype,
                    "name": os.path.basename(rel_path),
                    "summary": f"{rel_path} dosyası.",
                    "tags": [ftype]
                })

    # Add the tum_proje_kodlari.txt itself as a file node
    output_nodes.append({
        "id": "file:tum_proje_kodlari.txt",
        "type": "document",
        "name": "tum_proje_kodlari.txt",
        "summary": "Tüm proje kodlarını içeren toplu dosya.",
        "tags": ["source-dump"]
    })

    result = {
        "batchIndex": 1,
        "nodes": output_nodes,
        "edges": output_edges
    }
    
    with open(os.path.join(base_path, '.understand-anything', 'intermediate', 'batch-1.json'), 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    process_batch_1()
