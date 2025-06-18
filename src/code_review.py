from typing import List, Dict, Any, Union, Optional, Tuple
from dataclasses import dataclass
import re
import requests
import os
import json
import hashlib
from langchain.tools import StructuredTool
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

@dataclass
class CodeReviewConfig:
    """Configuration for code review parameters"""
    max_files_per_review: int = 10
    max_lines_per_file: int = 300
    ignore_file_patterns: List[str] = None
    review_aspects: List[str] = None

    def __post_init__(self):
        if self.ignore_file_patterns is None:
            self.ignore_file_patterns = [
                r".*\.lock$",
                r".*package-lock\.json$",
                r".*\.min\.(js|css)$",
                r".*/dist/.*",
                r".*/build/.*"
            ]
        if self.review_aspects is None:
            self.review_aspects = [
                "code_quality",
                "potential_bugs",
                "security",
                "performance",
                "maintainability"
            ]

class CodeReviewPipeline:
    """Pipeline for processing code reviews"""
    
    def __init__(self, config: CodeReviewConfig = None):
        self.config = config or CodeReviewConfig()
    
    
    def prepare_diff_content(self, diffs: List[Dict[str, Any]]) -> str:
        """Format diff content for review"""
        formatted_diffs = []
        for diff in diffs:
            file_path = diff.get("new_path") or diff.get("old_path")
            diff_content = diff.get("diff", "").strip()
            if diff_content:
                formatted_diffs.append(f"File: {file_path}\n```diff\n{diff_content}\n```\n")
        return "\n".join(formatted_diffs) if formatted_diffs else "No changes found in the diff"
    
    def _prepare_review_prompt(self, content: str) -> str:
        """
        Prepare the review prompt with formatted content and instructions for structured output.
        Optimized for single line comments with line range mentions.
        """
        return f"""As an expert code reviewer, analyze this merge request and provide actionable feedback focusing on critical production issues:
        {content}

        Focus ONLY on these critical aspects:
        1. Logic errors or bugs that could affect business logic
        2. Performance issues that could impact user experience
        3. Critical code style violations (e.g., naming that causes confusion, deeply nested code)
        4. Security vulnerabilities
        5. Breaking changes in APIs or interfaces

        DO NOT comment on:
        - Missing logs or tracking
        - Minor style issues
        - Missing comments or documentation
        - Test coverage (unless it's a critical flow)

        Output a JSON array with detailed comments using this format:
        [
          {{
            "position_type": "text",
            "new_path": "<file path after change>",
            "new_line": <start line number of the code block>,
            "old_path": "<file path before change>",
            "old_line": <Optional, start line number in old version, use when comparing with old code>,
            "comment": "AI Review [Lines <start>-<end>]: <detailed explanation of the issue, its impact, and suggested improvement>"
          }}
        ]

        Important notes for comments:
        1. When reviewing a function or code block:
           - new_line MUST point to the actual function/component definition line
           - [Lines X-Y] MUST cover the entire function/block being discussed, with X and Y being the start and end line numbers of the function/block
           - If discussing a specific line within a function, still point to function definition but mention the specific line in the comment
           - NEVER point to empty lines or import statements when discussing a component/function
        2. Place comment at the first line of the discussed code block
        3. Prefix all comments with "AI Review "
        4. Include only comments for code present in the diff
        5. Double check that line numbers in [Lines X-Y] correspond to the actual code being discussed

        Focus on making each comment:
        - Highlight potential production risks
        - Explain performance implications if any
        - Point out breaking changes or API inconsistencies
        - Suggest fixes for critical code style issues

        Example of good comment placement:
        ```typescript
        // Old version
        12  function handleData(data) {{
        
        // New version
        15  function processData(data) {{  // <- renamed function
        16    // Implementation
        25  }}
        ```
        Comment should be:
        {{
          "new_line": 15,  // Points to new function definition
          "old_line": 12,  // Points to old function definition
          "comment": "AI Review [Lines 15-25]: Function rename from 'handleData' to 'processData' may break existing callers. Ensure all call sites are updated."
        }}
        """

    
    async def get_related_code_from_agent(self, agent, vectorstore, diff_content: str, k: int = 3) -> str:
        """
        Ask the agent for the best keyword(s) to search for related code, then retrieve code snippets from the vectorstore.
        Now supports multiple keywords from the agent's response.
        """
        # Yêu cầu AI trả về nhiều keyword, mỗi keyword trên một dòng hoặc phân tách bởi dấu phẩy
        prompt = (
            "Given the following code diff, list all keywords, function names, or concepts that should be used to search for related code in the codebase. "
            "Return only the keywords, one per line or separated by commas. Do not explain.\n\n"
            f"Diff:\n{diff_content}"
        )
        agent_response = await agent.run(prompt)
        # Tách tất cả các keyword (theo dòng hoặc dấu phẩy)
        keywords = []
        for line in agent_response.strip().splitlines():
            keywords.extend([kw.strip() for kw in line.split(',') if kw.strip()])
        # Loại bỏ trùng lặp
        keywords = list(dict.fromkeys(keywords))
        # Lấy code liên quan cho từng keyword
        from rag_utils import get_related_code
        related_results = []
        print(f"Keywords: {keywords}")
        for kw in keywords:
            code = get_related_code(vectorstore, kw, k=1)
            if code:
                related_results.append(f"Keyword: {kw}\n{code}")
        return "\n\n".join(related_results)


    async def get_merge_request_info(self, agent, mr_iid: int, project_id: str) -> dict:
        """Get merge request changes, title, and description using direct GitLab API call (no Agent)"""
        try:
            # Use direct API call instead of agent
            raw = get_gitlab_mr_changes(project_id, mr_iid)
            # Remap to expected mr_data format
            mr_data = {
                "details": {
                    "title": raw.get("title", ""),
                    "description": raw.get("description", "")
                },
                "changes": raw.get("changes", [])
            }
            return mr_data
        except Exception as e:
            print(f"Error fetching merge request info: {e}")
            return None

    def format_mr_content(self, mr_info: Dict) -> str:
        """Format merge request content for review"""
        if not mr_info:
            return "Error: Could not fetch merge request information"

        details = mr_info.get('details', '')
        changes = mr_info.get('changes', '')

        # Convert details dict to string with title and description if needed
        if isinstance(details, dict):
            title = details.get('title', '')
            description = details.get('description', '')
            details = f"Title: {title}\nDescription: {description}"

        # Convert changes list to string if needed
        if isinstance(changes, list):
            changes = json.dumps(changes, indent=2, ensure_ascii=False)

        # Format content for review
        content = [
            "Merge Request Information:",
            "------------------------",
            details,
            "\nChanges:",
            "--------",
            changes
        ]

        return "\n".join(content)

    async def review_merge_request(self, agent, mr_iid: int, project_id: str, vectorstore=None) -> str:
        """Review a merge request and provide feedback"""
        print("\nFetching merge request information...")
        mr_info = await self.get_merge_request_info(agent, mr_iid, project_id)
        
        if not mr_info:
            return "Failed to fetch merge request information"

        # Prepare diff content from mr_info["changes"]
        diffs = mr_info.get("changes", [])
        diff_content = self.prepare_diff_content(diffs)
        review_content = self.format_mr_content(mr_info)

        # Get related code using the agent's suggestion (if vectorstore is provided)
        related_code = ""
        if vectorstore is not None:
            related_code = await self.get_related_code_from_agent(agent, vectorstore, diff_content)


        # Generate review using AI
        print("\nGenerating review...")
        review_prompt = self._prepare_review_prompt(review_content + "\n\nRelated Code:\n" + related_code)
        review = await agent.run(review_prompt)
        
        return review

    def _clean_json_response(self, response: str) -> str:
        """Clean response string by removing markdown code block markers and extracting JSON"""
        # Remove markdown code block markers if present
        if "```json" in response:
            response = response.split("```json")[1]
            if "```" in response:
                response = response.split("```")[0]
        
        # Find and extract JSON content
        json_start = response.find('{')
        if json_start != -1:
            response = response[json_start:]
            
        return response.strip()



def get_gitlab_mr_changes(project_id, mr_iid, api_url=None, api_token=None):
    """
    Get raw merge request changes from GitLab API directly (no Agent required).
    Returns the parsed JSON response.
    """
    api_url = api_url or os.getenv("GITLAB_API_URL", "https://gitlab.com/api/v4")
    api_token = api_token or os.getenv("GITLAB_API_TOKEN")
    url = f"{api_url}/projects/{project_id}/merge_requests/{mr_iid}/changes"
    headers = {"PRIVATE-TOKEN": api_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def extract_line_comments_from_review(review_text: str):
    """
    Extract the JSON array of line comments from the end of the AI review output.
    Returns a list of dicts with file, line, comment.
    """
    # Find the last JSON array in the text
    matches = re.findall(r'(\[\s*{[\s\S]*?}\s*\])', review_text)
    if not matches:
        return []
    try:
        comments = json.loads(matches[-1])
        # Validate structure
        if isinstance(comments, list) and all(isinstance(c, dict) for c in comments):
            return comments
    except Exception:
        pass
    return []

def get_gitlab_mr_diff_refs(project_id, mr_iid, api_url=None, api_token=None):
    """
    Lấy diff_refs (base_sha, start_sha, head_sha) từ GitLab API cho MR.
    """
    api_url = api_url or os.getenv("GITLAB_API_URL", "https://gitlab.com/api/v4")
    api_token = api_token or os.getenv("GITLAB_API_TOKEN")
    url = f"{api_url}/projects/{project_id}/merge_requests/{mr_iid}"
    headers = {"PRIVATE-TOKEN": api_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    diff_refs = response.json().get("diff_refs", {})
    base_sha = diff_refs.get("base_sha")
    start_sha = diff_refs.get("start_sha")
    head_sha = diff_refs.get("head_sha")
    return base_sha, start_sha, head_sha

def gitlab_create_merge_request_thread(
    project_id: str,
    merge_request_iid: int,
    body: str,
    position_type: str,
    new_path: str,
    old_path: str,
    base_sha: str,
    start_sha: str,
    head_sha: str,
    new_line: str,
    old_line: str,
    **kwargs
) -> str:
    """
    Call GitLab API to create an inline comment (thread) on a merge request.
    """
    api_url = os.getenv("GITLAB_API_URL", "https://gitlab.com/api/v4")
    api_token = os.getenv("GITLAB_API_TOKEN")
    url = f"{api_url}/projects/{project_id}/merge_requests/{merge_request_iid}/discussions"

    # Build position object
    position = {
        "position_type": position_type,
        "base_sha": base_sha,
        "start_sha": start_sha,
        "head_sha": head_sha,
        "new_path": new_path,
        "old_path": old_path,
        "new_line": new_line,
        "old_line": old_line
    }

    # Add optional fields if they exist in kwargs
    optional_fields = ["width", "height", "x", "y"]
    for field in optional_fields:
        if field in kwargs:
            position[field] = kwargs[field]

    # Handle line_range if it exists
    if "line_range" in kwargs:
        position["line_range"] = kwargs["line_range"]

    # Create request data
    data = {
        "body": body,
        "position": position
    }

    # Add created_at if provided
    if "created_at" in kwargs:
        data["created_at"] = kwargs["created_at"]

    headers = {
        "PRIVATE-TOKEN": api_token,
        "Content-Type": "application/json"
    }

    print(f"[MCP] Creating merge request thread with data: {json.dumps(data, indent=2)}")
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code >= 400:
        print(f"Error creating merge request thread. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        raise Exception(f"Failed to create merge request thread: {response.text}")
    
    return response.json()["id"]


def post_line_comments_direct(project_id, mr_iid, comments):
    """
    Gửi tất cả line comments lên GitLab MR bằng cách gọi trực tiếp hàm gitlab_create_merge_request_thread.
    Hàm này là đồng bộ (sync), KHÔNG dùng await khi gọi.
    Nếu muốn gọi trong async context, hãy dùng: await asyncio.to_thread(post_line_comments_direct, ...)
    """
    base_sha, start_sha, head_sha = get_gitlab_mr_diff_refs(project_id, mr_iid)
    if not (base_sha and start_sha and head_sha):
        print("Could not get diff_refs (base_sha, start_sha, head_sha) from MR API.")
        return

    print(f"[MCP] Posting {len(comments)} line comments to MR {mr_iid} in project {project_id} (direct API mode)...")
    for idx, c in enumerate(comments, 1):
        try:
            # Validate comment has required fields
            if not c.get("new_path") or not c.get("new_line") or not c.get("comment"):
                print(f"[MCP] Comment {idx}: Skipped - Missing required fields (need new_path, new_line, and comment). Data: {c}")
                continue

            # Build comment parameters
            comment_params = {
                "project_id": project_id,
                "merge_request_iid": mr_iid,
                "body": c["comment"],
                "position_type": c.get("position_type", "text"),
                "new_path": c["new_path"],
                "old_path": c["old_path"],
                "base_sha": base_sha,
                "start_sha": start_sha,
                "head_sha": head_sha,
                "new_line": c["new_line"],
                "old_line": c.get("old_line", None),
            }
            print("comment_params", comment_params)

            result = gitlab_create_merge_request_thread(**comment_params)
            print(f"[MCP] Comment {idx}: Success - {result}")
        except Exception as e:
            print(f"[MCP] Comment {idx}: Error - {e}")

# Example usage after getting review:
def debug_ai_review_and_comments(review):
    print("\n[DEBUG] Raw AI review output:\n" + "-"*40)
    print(review)
    comments = extract_line_comments_from_review(review)
    print("\n[DEBUG] Extracted line comments:")
    for c in comments:
        print(c)
    return comments 