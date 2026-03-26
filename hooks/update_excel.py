#!/usr/bin/env python3
"""
Post-tool-use hook to update Excel tracker when requirements are created or modified.
Automatically extracts YAML frontmatter from requirement markdown files and syncs to Excel.
"""

import sys
import json
import yaml
import re
from pathlib import Path
from datetime import datetime

def log(message):
    """Log to stderr so it doesn't interfere with hook output"""
    print(f"[update_excel.py] {message}", file=sys.stderr)

def extract_frontmatter(file_path):
    """Extract YAML frontmatter from markdown file"""
    try:
        content = Path(file_path).read_text()
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            log(f"No YAML frontmatter found in {file_path}")
            return None
        return yaml.safe_load(match.group(1))
    except Exception as e:
        log(f"Error extracting frontmatter: {e}")
        return None

def update_excel_tracker(metadata, file_path):
    """Update Excel tracker with requirement metadata"""
    try:
        # Import pandas only when needed (lazy import)
        import pandas as pd

        excel_path = Path("requirements/requirements_tracker.xlsx")

        # Load existing Excel or create new DataFrame
        if excel_path.exists():
            df = pd.read_excel(excel_path)
        else:
            df = pd.DataFrame(columns=["ID", "Name", "Description", "Status", "Priority", "Owner", "Related To", "Test Cases", "File Path", "Last Updated"])

        # Prepare new row data
        new_row = {
            "ID": metadata.get("id", ""),
            "Name": metadata.get("name", ""),
            "Description": metadata.get("description", ""),
            "Status": metadata.get("status", "draft"),
            "Priority": metadata.get("priority", ""),
            "Owner": metadata.get("owner", ""),
            "Related To": ", ".join(metadata.get("related_to", [])),
            "Test Cases": ", ".join(metadata.get("test_cases", [])),
            "File Path": file_path,
            "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Update if exists, append if new
        req_id = metadata.get("id")
        if not req_id:
            log("No requirement ID found, skipping Excel update")
            return False

        if not df.empty and "ID" in df.columns and req_id in df["ID"].values:
            # Update existing row
            idx = df[df["ID"] == req_id].index[0]
            for col, val in new_row.items():
                df.at[idx, col] = val
            action = "Updated"
        else:
            # Append new row
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            action = "Added"

        # Sort by ID
        df = df.sort_values("ID")

        # Save to Excel
        excel_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(excel_path, index=False, engine='openpyxl')

        print(f"✓ {action} {req_id} in requirements_tracker.xlsx")
        return True

    except ImportError:
        log("pandas or openpyxl not installed. Install with: pip install pandas openpyxl")
        return False
    except Exception as e:
        log(f"Error updating Excel: {e}")
        return False

def main():
    try:
        # Read the tool use event from stdin
        event = json.load(sys.stdin)

        params = event.get("params", {})
        file_path = params.get("file_path", "")

        # Only process requirement files
        if not re.match(r".*requirements/REQ-\d+.*\.md$", file_path):
            sys.exit(0)

        log(f"Processing requirement file: {file_path}")

        # Extract YAML frontmatter
        metadata = extract_frontmatter(file_path)
        if not metadata:
            sys.exit(0)

        # Update Excel tracker
        update_excel_tracker(metadata, file_path)

    except json.JSONDecodeError:
        log("Invalid JSON input from stdin")
        sys.exit(0)
    except Exception as e:
        log(f"Unexpected error: {e}")
        sys.exit(0)

if __name__ == "__main__":
    main()
