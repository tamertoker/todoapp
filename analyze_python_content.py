import ast
import json
import os

def analyze_file(file_path):
    if not os.path.exists(file_path):
        return [], []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return [], []

    nodes = []
    edges = []

    # File node
    file_id = f"file:{file_path}"
    # Determine type and tags
    node_type = "file"
    tags = ["python", "code"]
    if "repository" in file_path:
        node_type = "table" # represent database access
        tags.append("persistence")
    elif "servisi" in file_path or "service" in file_path:
        node_type = "service"
        tags.append("application")
    elif "domain" in file_path:
        tags.append("domain")
    elif "presentation" in file_path or "view" in file_path:
        tags.append("ui")
    
    # Layer
    layer = "Shared"
    if "domain" in file_path: layer = "Domain"
    elif "application" in file_path: layer = "Application"
    elif "infrastructure" in file_path: layer = "Infrastructure"
    elif "presentation" in file_path: layer = "Presentation"

    # Summary in Turkish
    # We can use the docstring if available
    docstring = ast.get_docstring(tree) or ""
    summary = docstring.split('\n')[0] if docstring else f"{os.path.basename(file_path)} dosyası."
    if not summary: summary = f"{os.path.basename(file_path)} dosyası."

    nodes.append({
        "id": file_id,
        "name": os.path.basename(file_path),
        "type": node_type,
        "filePath": file_path,
        "summary": summary,
        "tags": tags,
        "complexity": "simple" # placeholder
    })

    # Extract symbols
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_id = f"class:{file_path}:{node.name}"
            class_doc = ast.get_docstring(node) or ""
            class_summary = class_doc.split('\n')[0] if class_doc else f"{node.name} sınıfı."
            nodes.append({
                "id": class_id,
                "name": node.name,
                "type": "class",
                "filePath": file_path,
                "summary": class_summary,
                "tags": tags + ["class"]
            })
            edges.append({
                "source": class_id,
                "target": file_id,
                "type": "contains",
                "weight": 1.0
            })
            
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name.startswith('_') and item.name != '__init__': continue
                    func_id = f"function:{file_path}:{node.name}.{item.name}"
                    func_doc = ast.get_docstring(item) or ""
                    func_summary = func_doc.split('\n')[0] if func_doc else f"{node.name} içindeki {item.name} metodu."
                    nodes.append({
                        "id": func_id,
                        "name": item.name,
                        "type": "function",
                        "filePath": file_path,
                        "summary": func_summary,
                        "tags": tags + ["method"]
                    })
                    edges.append({
                        "source": func_id,
                        "target": class_id,
                        "type": "contains",
                        "weight": 1.0
                    })
        
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith('_'): continue
            func_id = f"function:{file_path}:{node.name}"
            func_doc = ast.get_docstring(node) or ""
            func_summary = func_doc.split('\n')[0] if func_doc else f"{node.name} fonksiyonu."
            nodes.append({
                "id": func_id,
                "name": node.name,
                "type": "function",
                "filePath": file_path,
                "summary": func_summary,
                "tags": tags + ["function"]
            })
            edges.append({
                "source": func_id,
                "target": file_id,
                "type": "contains",
                "weight": 1.0
            })

    # Basic import analysis
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith('leveltodo'):
                    # placeholder edge
                    pass
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith('leveltodo'):
                # placeholder edge
                pass

    return nodes, edges

def analyze_batch(batch_idx, files):
    all_nodes = []
    all_edges = []
    for f in files:
        nodes, edges = analyze_file(f)
        all_nodes.extend(nodes)
        all_edges.extend(edges)
    
    # Process edges from import data in batches.json if possible
    # But user wants me to be the analyzer.
    
    output = {
        "nodes": all_nodes,
        "edges": all_edges
    }
    
    os.makedirs(".understand-anything/intermediate", exist_ok=True)
    with open(f".understand-anything/intermediate/batch-{batch_idx}.json", "w", encoding="utf-8") as out:
        json.dump(output, out, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    import sys
    batch_idx = int(sys.argv[1])
    files = sys.argv[2:]
    analyze_batch(batch_idx, files)
