#!/bin/bash
# 1. Create venv
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize Wiki structure
echo "Initializing Requirements Wiki structure..."
codemie-claude -p "Execute the automatic setup check from @SYSTEM_PROMPT.md"

# 4. Inform the user
echo "Environment ready. Run 'claude' to start with the Requirements Tool active."