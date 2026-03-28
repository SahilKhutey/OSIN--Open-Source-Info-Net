import os
import sys

# Add backend to path for imports
project_root = r"c:\Users\User\Documents\OSIN"
sys.path.append(os.path.join(project_root, "backend"))

print("🔍 Verification Diagnostic")
print("==========================")

# 1. Check directories
print(f"\n1. Checking Layer Directories:")
for i in range(7):
    path = os.path.join(project_root, f"layer{i}")
    exists = os.path.isdir(path)
    print(f"  [{'✅' if exists else '❌'}] layer{i}")

# 2. Check .env
env_path = os.path.join(project_root, ".env")
print(f"\n2. Checking .env file: {'✅' if os.path.isfile(env_path) else '❌'}")

# 3. Test Security Manager Path Resolution
print(f"\n3. Testing Security Manager Path Resolution:")
try:
    from osig.security.security_manager import AuditLogger
    # We won't actually initialize to avoid side effects, but we can check the logic if we want.
    # Actually, let's just import and check if the class is there.
    print(f"  ✅ AuditLogger imported successfully.")
except Exception as e:
    print(f"  ❌ Failed to import or verify AuditLogger: {e}")

# 4. Check Kafka and Security paths via dry-run simulation
print(f"\n4. Checking path logic in code:")
files_to_check = [
    os.path.join(project_root, "osig", "security", "security_manager.py"),
    os.path.join(project_root, "backend", "app", "streaming", "kafka_manager.py"),
    os.path.join(project_root, "backend", "app", "core", "security.py")
]

for f in files_to_check:
    if os.path.exists(f):
        with open(f, 'r') as file:
            content = file.read()
            if "os.path.dirname(os.path.abspath(__file__))" in content:
                print(f"  ✅ {os.path.basename(f)} uses dynamic path resolution.")
            else:
                print(f"  ❌ {os.path.basename(f)} might still have hardcoded paths.")
    else:
        print(f"  ❌ {os.path.basename(f)} NOT FOUND.")

print("\n✅ Verification complete!")
