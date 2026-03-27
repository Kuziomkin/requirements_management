from mcp.server.fastmcp import FastMCP
from pydantic import Field
import pandas as pd
import json
from pathlib import Path
from typing import Optional
import re

mcp = FastMCP("RequirementsMCP", log_level="DEBUG")

@mcp.tool(
    name="create_requirement_tracker",
    description="Create a Excel tracker for requirements if it doesn't exist. Returns status of creation or existence. Call it before creating the requirement to ensure the tracker is set up."
)
def create_requirement_tracker(
        excel_path: str = Field(default="requirements/requirements_tracker.xlsx", description="Path to the Excel tracker file")
        ) -> str:
    """
    Creates an Excel tracker file with the appropriate structure if it doesn't already exist.
    """
    try:
        path = Path(excel_path)
        if path.exists():
            return json.dumps({
                "status": "exists",
                "message": f"Excel tracker already exists at {excel_path}"
            }, indent=2)

        # Create parent directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        # Create an empty DataFrame with the required columns
        df = pd.DataFrame(columns=["ID", "Name", "Description", "Status", "Priority", "Owner", "Related To", "Test Cases", "File Path", "Last Updated"])
        df.to_excel(path, index=False)

        return json.dumps({
            "status": "created",
            "message": f"Excel tracker created at {excel_path}"
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error creating Excel tracker: {str(e)}"
        }, indent=2)



@mcp.tool(
    name="analyze_requirements_tracker",
    description="Analyzes the requirements tracker Excel file to generate next REQ-ID and check for duplicate/conflicting requirements. Returns analysis results and recommendations for the new requirement based on the user's request. Call it with the user's requirement summary to get insights before creating a new requirement."
)
def analyze_requirements_tracker(
    user_request: str = Field(..., description="Summary of what the user wants to create a requirement for"),
    excel_path: str = Field(default="requirements/requirements_tracker.xlsx", description="Path to the Excel tracker file")
) -> str:
    """
    Reads the requirements tracker Excel, calculates next ID, and checks for duplicates/conflicts.

    Returns JSON with:
    - next_id: The REQ-XXX ID to use for the new requirement
    - analysis_status: none|duplicate_found|contradiction_found|related_found
    - conflicts: Array of conflicting requirements
    - related_requirements: Array of related requirements
    - recommendation: Action to take (proceed|update_existing|user_decision)
    """
    try:
        path = Path(excel_path)

        # If Excel doesn't exist yet, start with REQ-001
        if not path.exists():
            return json.dumps({
                "next_id": "REQ-001",
                "analysis_status": "none",
                "conflicts": [],
                "related_requirements": [],
                "recommendation": {
                    "action": "proceed",
                    "details": "No existing requirements found. Starting with REQ-001."
                }
            }, indent=2)

        # Read the Excel file
        df = pd.read_excel(excel_path)

        # Calculate next ID
        if df.empty or 'ID' not in df.columns:
            next_id = "REQ-001"
        else:
            # Extract numeric part from REQ-XXX format
            ids = df['ID'].dropna().astype(str)
            numeric_ids = []
            for id_val in ids:
                match = re.match(r'REQ-(\d+)', id_val)
                if match:
                    numeric_ids.append(int(match.group(1)))

            if numeric_ids:
                max_id = max(numeric_ids)
                next_id = f"REQ-{max_id + 1:03d}"
            else:
                next_id = "REQ-001"

        # Analyze for duplicates and conflicts
        conflicts = []
        related_requirements = []
        analysis_status = "none"

        if not df.empty:
            # Normalize user request for comparison
            user_request_lower = user_request.lower()

            for idx, row in df.iterrows():
                req_id = row.get('ID', '')
                name = str(row.get('Name', ''))
                description = str(row.get('Description', ''))

                # Simple keyword matching for duplicates/conflicts
                name_lower = name.lower()
                desc_lower = description.lower()

                # Check for exact or very similar names
                if name_lower and name_lower in user_request_lower:
                    conflicts.append({
                        "req_id": req_id,
                        "name": name,
                        "conflict_type": "duplicate",
                        "reason": f"Requirement name '{name}' appears to match the requested functionality"
                    })
                    analysis_status = "duplicate_found"

                # Check for keyword overlap (simple heuristic)
                user_keywords = set(word for word in user_request_lower.split() if len(word) > 4)
                desc_keywords = set(word for word in desc_lower.split() if len(word) > 4)
                overlap = user_keywords & desc_keywords

                if len(overlap) >= 2:  # At least 2 significant keyword matches
                    related_requirements.append({
                        "req_id": req_id,
                        "name": name,
                        "relationship": "related",
                        "reason": f"Shares keywords: {', '.join(list(overlap)[:3])}"
                    })
                    if analysis_status == "none":
                        analysis_status = "related_found"

        # Determine recommendation
        if conflicts:
            recommendation = {
                "action": "user_decision",
                "details": f"Found {len(conflicts)} potential duplicate(s). User should decide whether to proceed, update existing, or cancel."
            }
        elif related_requirements:
            recommendation = {
                "action": "proceed",
                "details": f"Found {len(related_requirements)} related requirement(s). Suggest adding to related_to field."
            }
        else:
            recommendation = {
                "action": "proceed",
                "details": "No conflicts detected. Safe to proceed with new requirement."
            }

        return json.dumps({
            "next_id": next_id,
            "analysis_status": analysis_status,
            "conflicts": conflicts,
            "related_requirements": related_requirements,
            "recommendation": recommendation
        }, indent=2)

    except Exception as e:
        # Return error in JSON format so subagent can handle it
        return json.dumps({
            "error": str(e),
            "next_id": "REQ-001",
            "analysis_status": "error",
            "conflicts": [],
            "related_requirements": [],
            "recommendation": {
                "action": "proceed",
                "details": f"Error analyzing tracker: {str(e)}. Defaulting to REQ-001."
            }
        }, indent=2)
    
    
@mcp.resource(
    uri="requirements://list",
    name="Get all requirements documents",
    description="Returns a list of all requirements documents in the tracker."
)
def get_all_requirements_documents() -> str:
    """
    Scans the requirements directory and returns a list of all requirement document paths as JSON.
    """
    try:
        req_docs = []
        for path in Path("requirements").rglob("REQ-*.md"):
            req_docs.append(str(path))
        return json.dumps({
            "requirements": req_docs,
            "count": len(req_docs)
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "requirements": [],
            "count": 0
        }, indent=2)
    


if __name__ == "__main__":
    mcp.run()