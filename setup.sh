#!/bin/bash
# 1. Create venv
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Inform the user
echo "Environment ready. Run 'claude' to start with the Requirements Tool active."