from typing import List, Dict, Any
from dataclasses import dataclass
import re
import requests
import os
import json
import hashlib

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
    
    def _prepare_review_prompt(self, content: str, file_to_lines: dict = None) -> str:
        """
        Prepare the review prompt with formatted content and instructions for structured output.
        Optionally include visible lines info for each file.
        """
        visible_lines_info = ""
        if file_to_lines:
            visible_lines_info = "\n".join(
                f"{file}: {sorted(list(lines))}" for file, lines in file_to_lines.items()
            )
            visible_lines_info = f"\nOnly comment on these visible lines in the diff:\n{visible_lines_info}\nIf you need more context to understand the scope or impact of a change (e.g., to check how a function is used, or to clarify dependencies), you MAY use the `query_codebase` tool to search the codebase for related code, definitions, or usages. If need know more about the merge request, you MAY use the `gitlab_get_merge_request` tool to get more context.\n"
        return f"""As an expert code reviewer, analyze this merge request and provide actionable feedback focusing on critical production issues:
        {content}
        {visible_lines_info}
        Focus ONLY on these critical aspects:
        1. Logic errors or bugs that could affect business logic
        2. Performance issues that could impact user experience
        3. Critical code style violations (e.g., naming that causes confusion, deeply nested code)

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
            "line": "<start line number of the code block at new_path>",
            "old_path": "<file path before change>",
            "comment": "AI Review [Lines <start>-<end>]: <detailed explanation into 3 parts: issue, its impact, and suggested improvement>",
            "isUseQueryCodebase": <boolean, true if you used the query_codebase tool to get more context>,
          }}
        ]

        Important notes for comments:
        1. When reviewing a function or code block:
           - [Lines X-Y] MUST cover the entire function/block being discussed, with X and Y being the start and end line numbers of the function/block
           - line MUST point to the actual function/component definition line
        2. Prefix all comments with "AI Review "
        4. Include only comments for code present in the diff
        *IMPORTANT: MUST DOUBLE CHECK that line numbers in [Lines X-Y] correspond to the actual code being discussed*

        Focus on making each comment:
        - Highlight potential production risks
        - Explain performance implications if any
        - Point out breaking changes or API inconsistencies
        - Suggest fixes for critical code style issues

        Example of good comment placement:
        ```typescript
        // Old version
        12 - function handleData(data) {{  // <- deleted function
        // New version
        15 + function processData(data) {{  // <- renamed function
        16 +    // Implementation
        25 +  }}
        Comment should be:
        {{
          "line": 15,  // Points to new function definition
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

    async def review_merge_request(self, agent, mr_iid: int, project_id: str, vectorstore=None):
        """Review a merge request and provide feedback. Returns (review, mr_info)."""
        print("\nFetching merge request information...")
        mr_info = await self.get_merge_request_info(agent, mr_iid, project_id)
        if not mr_info:
            return "Failed to fetch merge request information", None
        # Prepare diff content from mr_info["changes"]
        diffs = mr_info.get("changes", [])
        diff_content = self.prepare_diff_content(diffs)
        review_content = self.format_mr_content(mr_info)
        file_to_lines = get_all_commentable_lines_from_mr_diffs(mr_info.get("changes", []))
        print(f"file_to_lines: {file_to_lines}")
        # Generate review using AI, passing file_to_lines for visible lines info
        print("\nGenerating review...")
        review_prompt = self._prepare_review_prompt(review_content, file_to_lines)
        review = await agent.run(review_prompt)
        return review, mr_info

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

def calculate_file_sha1(file_path: str) -> str:
    """
    Calculate SHA1 hash of file path as GitLab does.
    """
    return hashlib.sha1(file_path.encode('utf-8')).hexdigest()

def generate_line_code(file_path: str, old_line: int = None, new_line: int = 0) -> str:
    file_sha = calculate_file_sha1(file_path)
    # For new files, old_line must be None or 0, but GitLab expects null in the API, so use 0 in the string
    return f"{file_sha}_{old_line if old_line is not None else 0}_{new_line or 0}"

def gitlab_create_merge_request_thread(
    project_id: str,
    merge_request_iid: int,
    body: str,
    position_type: str,
    base_sha: str,
    start_sha: str,
    head_sha: str,
    new_path: str = None,
    old_path: str = None,
    new_line: int = None,
    old_line: int = None,
    **kwargs
) -> str:
    """
    Call GitLab API to create an inline comment (thread) on a merge request.
    Always include line_code if possible. For new files, old_line must be None.
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
      
    }
    position["new_line"] = new_line
    position["old_line"] = old_line
    # position["line_code"] = generate_line_code(new_path, new_line, None)
    if new_path:
        position["new_path"] = new_path
    if old_path:
        position["old_path"] = old_path
    # if new_line is not None:
    #     position["new_line"] = new_line
    # # For new files, old_line must be None
    # if old_line is not None:
    #     position["old_line"] = old_line
    # # Always add line_code if new_path and new_line are present
    # if new_path and new_line is not None:
    #     position["line_code"] = generate_line_code(new_path, old_line, new_line)

    # Add optional fields if they exist in kwargs
    optional_fields = ["width", "height", "x", "y"]
    for field in optional_fields:
        if field in kwargs:
            position[field] = kwargs[field]

    # Create request data
    data = {
        "body": body,
        "position": position
    }
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

def build_line_type_mapping_from_diff(diff_json):
    """
    Build a mapping: (file_path, new_line) -> type ('new', 'deleted', 'unchanged')
    """
    mapping = {}
    for file_diff in diff_json:
        file_path = file_diff['new_path']
        diff_text = file_diff.get('diff', '')
        old_line = None
        new_line = None
        for line in diff_text.splitlines():
            if line.startswith('@@'):
                parts = line.split(' ')
                old_range = parts[1]  # e.g. -53,7
                new_range = parts[2]  # e.g. +55,7
                old_start = int(old_range.split(',')[0][1:])
                new_start = int(new_range.split(',')[0][1:])
                old_line = old_start
                new_line = new_start
            elif line.startswith('+') and not line.startswith('+++'):
                mapping[(file_path, new_line)] = "new"
                new_line += 1
            elif line.startswith('-') and not line.startswith('---'):
                mapping[(file_path, old_line)] = "deleted"
                old_line += 1
            else:
                mapping[(file_path, new_line)] = "unchanged"
                old_line += 1
                new_line += 1
    return mapping

def build_line_mapping_from_diff(diff_json):
    """
    Build a mapping: (file_path, new_line) -> old_line (or None if not available)
    """
    mapping = {}
    for file_diff in diff_json:
        file_path = file_diff['new_path']
        diff_text = file_diff.get('diff', '')
        old_line = None
        new_line = None
        for line in diff_text.splitlines():
            if line.startswith('@@'):
                parts = line.split(' ')
                old_range = parts[1]  # e.g. -53,7
                new_range = parts[2]  # e.g. +55,7
                old_start = int(old_range.split(',')[0][1:])
                new_start = int(new_range.split(',')[0][1:])
                old_line = old_start
                new_line = new_start
            elif line.startswith('+') and not line.startswith('+++'):
                # Added line: no old_line
                mapping[(file_path, new_line)] = None
                new_line += 1
            elif line.startswith('-') and not line.startswith('---'):
                # Deleted line: no new_line
                old_line += 1
            else:
                # Context line: mapping 1-1
                mapping[(file_path, new_line)] = old_line
                old_line += 1
                new_line += 1
    return mapping

def post_line_comments_direct(project_id, mr_iid, comments, diffs=None):
    """
    Post all line comments to GitLab MR by calling gitlab_create_merge_request_thread directly.
    Always generate and include line_code. For new files, set old_line to None.
    Accepts optional 'diffs' to avoid redundant API calls.
    """
    base_sha, start_sha, head_sha = get_gitlab_mr_diff_refs(project_id, mr_iid)
    if not (base_sha and start_sha and head_sha):
        print("Could not get diff_refs (base_sha, start_sha, head_sha) from MR API.")
        return

    # Use provided diffs if available, otherwise fetch from API
    if diffs is not None:
        line_type_mapping = build_line_type_mapping_from_diff(diffs)
        line_mapping = build_line_mapping_from_diff(diffs)
    else:
        from .code_review import get_gitlab_mr_changes  # avoid circular import if any
        mr_info = get_gitlab_mr_changes(project_id, mr_iid)
        diffs = mr_info.get("changes", [])
        line_type_mapping = build_line_type_mapping_from_diff(diffs)
        line_mapping = build_line_mapping_from_diff(diffs)

    print(f"[MCP] Posting {len(comments)} line comments to MR {mr_iid} in project {project_id} (direct API mode)...")
    for idx, c in enumerate(comments, 1):
        try:
            if not c.get("new_path") or not c.get("line") or not c.get("comment"):
                print(f"[MCP] Comment {idx}: Skipped - Missing required fields (need new_path, line, and comment). Data: {c}")
                continue
           
            if not c.get("type"):
                key = (c["new_path"], c["line"])
                c["type"] = line_type_mapping.get(key)
                print(f"[DEBUG] Comment {idx}: key={key}, detected type={c['type']}, comment={c['comment']}")
                if c["type"] is None:
                    print(f"[WARNING] Could not determine type for comment {idx} at {key}. Comment will be posted without type-based line logic.")
            else:
                print(f"[DEBUG] Comment {idx}: type already set to {c['type']}, key=({c['new_path']}, {c['line']})")
            # For deleted or unchanged, try to fill old_line if missing
            if c.get("type") in ("deleted", "unchanged"):
                key = (c["new_path"], c["line"])
                mapped_old_line = line_mapping.get(key)
                if mapped_old_line is not None:
                    c["old_line"] = mapped_old_line
                    print(f"[DEBUG] Comment {idx}: Filled old_line={mapped_old_line} for key={key}")
                else:
                    print(f"[WARNING] Comment {idx}: Could not find old_line for key={key}")
            comment_params = {
                "project_id": project_id,
                "merge_request_iid": mr_iid,
                "body": c["comment"],
                "position_type": c.get("position_type", "text"),
                "new_path": c["new_path"],
                "old_path": c.get("old_path"),
                "base_sha": base_sha,
                "start_sha": start_sha,
                "head_sha": head_sha,
                "new_line": c["line"],
                "old_line": c.get("old_line"),
                "type": c.get("type"),
            }
            # line_code will be generated in gitlab_create_merge_request_thread
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

def extract_commentable_lines_from_diff(diff_text: str) -> set:
    """
    Given a unified diff string, return a set of new line numbers that are visible/commentable in the diff.
    """
    commentable_lines = set()
    new_line_num = None
    for line in diff_text.splitlines():
        if line.startswith('@@'):
            # Example: @@ -1,7 +1,7 @@
            parts = line.split(' ')
            new_range = parts[2]  # e.g. '+1,7'
            new_start = int(new_range.split(',')[0][1:])
            new_line_num = new_start
        elif line.startswith('+') and not line.startswith('+++'):
            commentable_lines.add(new_line_num)
            new_line_num += 1
        elif not line.startswith('-') and not line.startswith('---'):
            if new_line_num is not None:
                commentable_lines.add(new_line_num)
                new_line_num += 1
    return commentable_lines


def get_all_commentable_lines_from_mr_diffs(mr_diffs) -> dict:
    """
    Given the result from mcp_gitlab_get_merge_request_diffs, return a dict:
    { file_path: set([commentable_new_lines]) }
    """
    file_to_lines = {}
    for file_diff in mr_diffs:
        file_path = file_diff['new_path']
        diff_text = file_diff['diff']
        file_to_lines[file_path] = extract_commentable_lines_from_diff(diff_text)
    return file_to_lines


def filter_comments_to_visible_lines(comments, file_to_lines):
    """
    Only keep comments where new_line is in the set of commentable lines for that file.
    """
    filtered = []
    for c in comments:
        file_path = c.get('new_path')
        new_line = c.get('new_line')
        if file_path in file_to_lines and new_line in file_to_lines[file_path]:
            filtered.append(c)
    return filtered

def map_to_nearest_commentable_line(file_path, new_line, file_to_lines):
    """
    Map new_line to the nearest commentable line <= new_line in file_to_lines[file_path].
    """
    if file_path not in file_to_lines:
        return None
    lines = sorted(file_to_lines[file_path])
    # Find the largest line <= new_line
    valid_lines = [l for l in lines if l <= new_line]
    if not valid_lines:
        return None
    return valid_lines[-1]

def adjust_comments_to_nearest_visible(comments, file_to_lines):
    """
    For each comment, if new_line is not visible, map to nearest visible line above.
    """
    adjusted = []
    for c in comments:
        file_path = c.get('new_path')
        new_line = c.get('new_line')
        mapped_line = map_to_nearest_commentable_line(file_path, new_line, file_to_lines)
        if mapped_line is not None:
            c = c.copy()
            c['new_line'] = mapped_line
            adjusted.append(c)
    return adjusted

# def build_linecode_mapping_from_diff(diff_json):
#     """
#     Build a mapping: (file_path, side, line_number) -> line_code
#     side: 'new' for new file (right), 'old' for old file (left)
#     """
#     mapping = {}
#     for file_diff in diff_json:
#         file_path = file_diff['new_path']
#         # Parse the diff hunks if available (simulate GitLab API structure)
#         # If not available, fallback to parsing the unified diff
#         # Here, we parse the unified diff for context
#         diff_text = file_diff.get('diff', '')
#         old_line = None
#         new_line = None
#         for line in diff_text.splitlines():
#             if line.startswith('@@'):
#                 # Example: @@ -53,7 +55,7 @@
#                 parts = line.split(' ')
#                 old_range = parts[1]  # e.g. -53,7
#                 new_range = parts[2]  # e.g. +55,7
#                 old_start = int(old_range.split(',')[0][1:])
#                 new_start = int(new_range.split(',')[0][1:])
#                 old_line = old_start
#                 new_line = new_start
#             elif line.startswith('+') and not line.startswith('+++'):
#                 # Added line (right only)
#                 mapping[(file_path, 'new', new_line)] = None  # line_code to be filled later
#                 new_line += 1
#             elif line.startswith('-') and not line.startswith('---'):
#                 # Removed line (left only)
#                 mapping[(file_path, 'old', old_line)] = None
#                 old_line += 1
#             else:
#                 # Context line (both sides)
#                 mapping[(file_path, 'new', new_line)] = None
#                 mapping[(file_path, 'old', old_line)] = None
#                 old_line += 1
#                 new_line += 1
#     return mapping

# def find_best_line_for_comment(file_path, new_line, mapping):
#     """
#     Prefer new_line (right), fallback to old_line (left/context) if available.
#     Returns (side, line_number) or None.
#     """
#     if (file_path, 'new', new_line) in mapping:
#         return ('new', new_line)
#     # Try fallback to old_line (context)
#     if (file_path, 'old', new_line) in mapping:
#         return ('old', new_line)
#     # Try nearest above
#     for offset in range(1, 5):
#         if (file_path, 'new', new_line - offset) in mapping:
#             return ('new', new_line - offset)
#         if (file_path, 'old', new_line - offset) in mapping:
#             return ('old', new_line - offset)
#     return None

# def adjust_comments_to_gitlab_side_and_linecode(comments, mapping, generate_line_code_func):
#     """
#     For each comment, map to the best side/line and generate the correct line_code.
#     """
#     adjusted = []
#     for c in comments:
#         file_path = c.get('new_path')
#         new_line = c.get('new_line')
#         result = find_best_line_for_comment(file_path, new_line, mapping)
#         if result is not None:
#             side, mapped_line = result
#             c = c.copy()
#             c['new_line'] = mapped_line if side == 'new' else None
#             c['old_line'] = mapped_line if side == 'old' else None
#             # Generate line_code for this mapping
#             if side == 'new':
#                 c['line_code'] = generate_line_code_func(file_path, None, mapped_line)
#             else:
#                 c['line_code'] = generate_line_code_func(file_path, mapped_line, None)
#             adjusted.append(c)
#     return adjusted

# Usage in pipeline:
# 1. diffs = ... # get from mcp_gitlab_get_merge_request_diffs
# 2. mapping = build_linecode_mapping_from_diff(diffs)
# 3. adjusted_comments = adjust_comments_to_gitlab_side_and_linecode(ai_comments, mapping, generate_line_code)
# 4. post_line_comments_direct(project_id, mr_iid, adjusted_comments) 