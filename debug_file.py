from pathlib import Path

def debug_file(filepath):
    print(f"=== Debugging {filepath} ===")
    path = Path(filepath)
    
    print(f"Exists: {path.exists()}")
    print(f"Size: {path.stat().st_size} bytes")
    print(f"Permissions: {oct(path.stat().st_mode)}")
    
    # Try different ways to read
    print("\n--- Reading as binary ---")
    with open(filepath, 'rb') as f:
        binary_content = f.read()
        print(f"Binary length: {len(binary_content)}")
        print(f"First 50 bytes: {binary_content[:50]}")
    
    print("\n--- Reading as text ---")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text_content = f.read()
            print(f"Text length: {len(text_content)}")
            print(f"Content: '{text_content}'")
    except Exception as e:
        print(f"UTF-8 failed: {e}")
    
    # Try other encodings
    for encoding in ['utf-16', 'latin-1', 'cp1252']:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()
                if content.strip():
                    print(f"Found content with {encoding}: '{content[:100]}'")
        except:
            pass

# Check the problematic file
debug_file('src/core/image_loader.py')