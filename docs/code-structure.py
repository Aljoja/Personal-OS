import os
import ast

def get_function_calls(tree):
    """Extract function calls from AST"""
    calls = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)
    return calls

def analyze_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            content = f.read()
            tree = ast.parse(content)
            classes = []
            functions = []
            
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            calls = get_function_calls(item)
                            methods.append((item.name, calls))
                    classes.append((node.name, methods))
                elif isinstance(node, ast.FunctionDef):
                    calls = get_function_calls(node)
                    functions.append((node.name, calls))
            
            return classes, functions
        except Exception as e:
            return [], []

def print_structure(path, prefix="", is_last=True):
    try:
        items = sorted(os.listdir(path))
    except PermissionError:
        return
    
    items = [i for i in items if not i.startswith('.') and i != '__pycache__' and i != 'venv' and i != '.git']
    
    for i, item in enumerate(items):
        is_last_item = (i == len(items) - 1)
        item_path = os.path.join(path, item)
        
        connector = "└── " if is_last_item else "├── "
        print(f"{prefix}{connector}{item}")
        
        if os.path.isdir(item_path):
            extension = "    " if is_last_item else "│   "
            print_structure(item_path, prefix + extension, is_last_item)
        elif item.endswith('.py'):
            extension = "    " if is_last_item else "│   "
            classes, functions = analyze_file(item_path)
            
            for cls_name, methods in classes:
                print(f"{prefix}{extension}  └─ Class: {cls_name}")
                for method_name, calls in methods:
                    call_str = f" → calls: {', '.join(sorted(calls))}" if calls else ""
                    print(f"{prefix}{extension}      └─ {method_name}(){call_str}")
            
            for func_name, calls in functions:
                call_str = f" → calls: {', '.join(sorted(calls))}" if calls else ""
                print(f"{prefix}{extension}  └─ {func_name}(){call_str}")

if __name__ == "__main__":
    import sys
    start_path = sys.argv[1] if len(sys.argv) > 1 else "."
    print(f"{os.path.basename(os.path.abspath(start_path))}/")
    print_structure(start_path)