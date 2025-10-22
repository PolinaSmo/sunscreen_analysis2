import os
print(f"File exists: {os.path.exists('src/core/image_loader.py')}")
print(f"File size: {os.path.getsize('src/core/image_loader.py')}")

with open('src/core/image_loader.py', 'rb') as f:
    content = f.read()
    print(f"Binary content length: {len(content)}")
    print(f"First 100 bytes: {content[:100]}")
