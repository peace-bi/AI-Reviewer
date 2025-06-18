from typing import List, Dict, Any, Union
from dataclasses import dataclass
import re
import requests
import os
import json

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
        """Prepare the review prompt with formatted content and instructions for structured output"""
        return f"""As expert in code review, please review this merge request and provide feedback:
        {content}
        Provide a concise but thorough code review focusing on:
        1. Code quality and best practices
        2. Potential bugs or issues
        3. Security concerns
        4. Performance implications
        5. Suggestions for improvement

        Format your response as a clear, professional code review comment.

        ---
        For any specific line comments or suggestions, output a JSON array at the end of your review, with each item in the following format:
        [
          {{
            "position_type": "<position type, text or image>",
            "new_path": "<file path after change>",
            "new_line": <line number after change>,
            "old_path": "<file path before change, optional>",
            "old_line": <line number before change, optional>,
            "line_range": {{
                "start": {{"type": "new", "new_line": 10}},
                "end": {{"type": "new", "new_line": 15}}
            }},
            "comment": "AI Review: <your comment>"
          }}
        ]
        position_type must be required.
        If the comment is for a multiline range, use "line_range" as above. If for a single line, use "new_line" instead of "line_range".
        Only include this JSON if you have specific line comments. 
        The comment should be in the format of "AI Review: <your comment>". 
        Do not add explanations outside the JSON block.
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

async def post_line_comments_with_mcp(agent, project_id, mr_iid, comments):
    """
    Post each line comment to GitLab MR using MCP agent and gitlab_create_merge_request_thread tool.
    comments: list of dicts with position fields and comment.
    Strictly require AI to only use gitlab_create_merge_request_thread and only include non-None fields.
    Support multiline comments via line_range.
    """
    # Lấy diff_refs
    base_sha, start_sha, head_sha = get_gitlab_mr_diff_refs(project_id, mr_iid)
    if not (base_sha and start_sha and head_sha):
        print("Could not get diff_refs (base_sha, start_sha, head_sha) from MR API.")
        return

    print(f"[MCP] Posting {len(comments)} line comments to MR {mr_iid} in project {project_id}...")
    for c in comments:
        comment = c.get("comment")
        if not comment:
            print(f"[MCP] Skipping invalid comment: {c}")
            continue
        prompt = (
            "Use `gitlab_create_merge_request_thread` tool\n"
            "After calling the tool, you must output 'Final Answer: Comment posted' and stop.\n"
            "If you encounter an error, output 'Final Answer: Error - <error message>' and stop.\n"
            "Do not call the tool again for the same comment.\n"
            "Do not use any other tool or endpoint.\n"
            "with parameters: \n"
            f"project_id: {project_id}\n"
            f"merge_request_iid: {mr_iid}\n"
            f"body: {comment}\n"
            f"new_path: {c.get('new_path')}\n"
            f"new_line: {c.get('new_line')}\n"
            f"position_type: {c.get('position_type')}\n"
            f"base_sha: {base_sha}\n"
            f"start_sha: {start_sha}\n"
            f"head_sha: {head_sha}\n"
            f"line_range: {c.get('line_range')}\n"
            "Anything None value must be excluded from request."
        )
        print(f"[MCP] Posting prompt: {prompt}")
        response = await agent.run(prompt)
        print(f"[MCP] Response: {response}")

# Example usage after getting review:
def debug_ai_review_and_comments(review):
    print("\n[DEBUG] Raw AI review output:\n" + "-"*40)
    print(review)
    comments = extract_line_comments_from_review(review)
    print("\n[DEBUG] Extracted line comments:")
    for c in comments:
        print(c)
    return comments 