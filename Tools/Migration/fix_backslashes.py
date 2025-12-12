import re

# Read the file
with open(r'c:\EzeeGenie\web-app\Tools\Migration\migration.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace 4 backslashes with 2 backslashes for all LaTeX commands
content = re.sub(r"'\\\\\\\\(sum|prod|int|iint|iiint|oint|bigcup|bigcap|bigoplus|bigotimes)'", r"'\\\\\\1'", content)

# Write back
with open(r'c:\EzeeGenie\web-app\Tools\Migration\migration.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed backslashes in migration.py")
