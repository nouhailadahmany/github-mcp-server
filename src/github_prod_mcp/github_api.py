from __future__ import annotations

import base64
from typing import Any

import httpx

from github_prod_mcp.config import Settings


class GitHubApiError(Exception):
    def __init__(self, status_code: int, message: str, details: Any | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.details = details


class GitHubApiClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {settings.github_token}",
            "X-GitHub-Api-Version": settings.github_api_version,
            "User-Agent": settings.github_user_agent,
        }

    def _build_url(self, path: str) -> str:
        return f"{self._settings.github_api_base_url.rstrip('/')}/{path.lstrip('/')}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        try:
            with httpx.Client(
                timeout=self._settings.github_timeout_seconds,
                headers=self._headers,
            ) as client:
                response = client.request(
                    method=method,
                    url=self._build_url(path),
                    params=params,
                    json=json_body,
                )
        except httpx.TimeoutException as exc:
            raise GitHubApiError(504, "GitHub API request timed out") from exc
        except httpx.HTTPError as exc:
            raise GitHubApiError(502, f"GitHub API transport error: {exc}") from exc

        if response.status_code >= 400:
            details: Any
            try:
                details = response.json()
            except ValueError:
                details = response.text
            message = "GitHub API request failed"
            if isinstance(details, dict) and details.get("message"):
                message = str(details["message"])
            raise GitHubApiError(response.status_code, message, details)

        if response.status_code == 204 or not response.content:
            return {"status_code": response.status_code}

        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json()
        return {"raw": response.text}

    def get_authenticated_user(self) -> Any:
        return self._request("GET", "/user")

    def create_repository(self, payload: dict[str, Any]) -> Any:
        return self._request("POST", "/user/repos", json_body=payload)

    def get_repository(self, owner: str, repo: str) -> Any:
        return self._request("GET", f"/repos/{owner}/{repo}")

    def list_branches(self, owner: str, repo: str) -> Any:
        return self._request("GET", f"/repos/{owner}/{repo}/branches")

    def get_branch(self, owner: str, repo: str, branch: str) -> Any:
        return self._request("GET", f"/repos/{owner}/{repo}/branches/{branch}")

    def get_file_content(self, owner: str, repo: str, path: str, ref: str | None = None) -> Any:
        params = {"ref": ref} if ref else None
        return self._request("GET", f"/repos/{owner}/{repo}/contents/{path}", params=params)

    def list_repository_files(
        self,
        owner: str,
        repo: str,
        path: str | None = None,
        ref: str | None = None,
    ) -> Any:
        params = {"ref": ref} if ref else None
        normalized_path = path.strip("/") if path else ""
        endpoint = f"/repos/{owner}/{repo}/contents/{normalized_path}" if normalized_path else f"/repos/{owner}/{repo}/contents"
        return self._request("GET", endpoint, params=params)

    def get_readme(self, owner: str, repo: str) -> Any:
        return self._request("GET", f"/repos/{owner}/{repo}/readme")

    def search_repositories(
        self,
        query: str,
        sort: str | None,
        order: str | None,
        per_page: int,
        page: int,
    ) -> Any:
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": per_page,
            "page": page,
        }
        return self._request("GET", "/search/repositories", params={k: v for k, v in params.items() if v is not None})

    def search_code(
        self,
        query: str,
        sort: str | None,
        order: str | None,
        per_page: int,
        page: int,
    ) -> Any:
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": per_page,
            "page": page,
        }
        return self._request("GET", "/search/code", params={k: v for k, v in params.items() if v is not None})

    def search_issues(
        self,
        query: str,
        sort: str | None,
        order: str | None,
        per_page: int,
        page: int,
    ) -> Any:
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": per_page,
            "page": page,
        }
        return self._request("GET", "/search/issues", params={k: v for k, v in params.items() if v is not None})

    def list_issues(self, owner: str, repo: str) -> Any:
        return self._request("GET", f"/repos/{owner}/{repo}/issues")

    def get_issue(self, owner: str, repo: str, issue_number: int) -> Any:
        return self._request("GET", f"/repos/{owner}/{repo}/issues/{issue_number}")

    def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str | None,
        assignees: list[str] | None,
        labels: list[str] | None,
        milestone: int | None,
    ) -> Any:
        payload = {
            "title": title,
            "body": body,
            "assignees": assignees,
            "labels": labels,
            "milestone": milestone,
        }
        return self._request("POST", f"/repos/{owner}/{repo}/issues", json_body={k: v for k, v in payload.items() if v is not None})

    def update_issue(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        payload: dict[str, Any],
    ) -> Any:
        return self._request("PATCH", f"/repos/{owner}/{repo}/issues/{issue_number}", json_body=payload)

    def create_issue_comment(self, owner: str, repo: str, issue_number: int, body: str) -> Any:
        return self._request(
            "POST",
            f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
            json_body={"body": body},
        )

    def list_pull_requests(self, owner: str, repo: str) -> Any:
        return self._request("GET", f"/repos/{owner}/{repo}/pulls")

    def get_pull_request(self, owner: str, repo: str, pull_number: int) -> Any:
        return self._request("GET", f"/repos/{owner}/{repo}/pulls/{pull_number}")

    def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str,
        body: str | None,
        maintainer_can_modify: bool,
        draft: bool,
    ) -> Any:
        payload = {
            "title": title,
            "head": head,
            "base": base,
            "body": body,
            "maintainer_can_modify": maintainer_can_modify,
            "draft": draft,
        }
        return self._request("POST", f"/repos/{owner}/{repo}/pulls", json_body=payload)

    def merge_pull_request(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        commit_title: str | None,
        commit_message: str | None,
        merge_method: str,
    ) -> Any:
        payload = {
            "commit_title": commit_title,
            "commit_message": commit_message,
            "merge_method": merge_method,
        }
        return self._request(
            "PUT",
            f"/repos/{owner}/{repo}/pulls/{pull_number}/merge",
            json_body={k: v for k, v in payload.items() if v is not None},
        )

    def get_commit(self, owner: str, repo: str, ref: str) -> Any:
        return self._request("GET", f"/repos/{owner}/{repo}/commits/{ref}")

    def compare_commits(self, owner: str, repo: str, basehead: str) -> Any:
        return self._request("GET", f"/repos/{owner}/{repo}/compare/{basehead}")

    def create_or_update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        message: str,
        content: str,
        branch: str | None,
        sha: str | None,
        committer: dict[str, str] | None,
        author: dict[str, str] | None,
    ) -> Any:
        payload = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
            "branch": branch,
            "sha": sha,
            "committer": committer,
            "author": author,
        }
        return self._request(
            "PUT",
            f"/repos/{owner}/{repo}/contents/{path}",
            json_body={k: v for k, v in payload.items() if v is not None},
        )

    def append_to_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str | None,
        committer: dict[str, str] | None,
        author: dict[str, str] | None,
    ) -> Any:
        # First, get the current file content and SHA
        file_info = self.get_file_content(owner, repo, path, branch)
        
        # Decode the existing content
        existing_content = base64.b64decode(file_info["content"]).decode("utf-8")
        
        # Append new content
        updated_content = existing_content + content
        
        # Update the file with appended content
        payload = {
            "message": message,
            "content": base64.b64encode(updated_content.encode("utf-8")).decode("utf-8"),
            "sha": file_info["sha"],
            "branch": branch,
            "committer": committer,
            "author": author,
        }
        return self._request(
            "PUT",
            f"/repos/{owner}/{repo}/contents/{path}",
            json_body={k: v for k, v in payload.items() if v is not None},
        )

    def delete_file(
        self,
        owner: str,
        repo: str,
        path: str,
        message: str,
        sha: str,
        branch: str | None,
        committer: dict[str, str] | None,
        author: dict[str, str] | None,
    ) -> Any:
        payload = {
            "message": message,
            "sha": sha,
            "branch": branch,
            "committer": committer,
            "author": author,
        }
        return self._request(
            "DELETE",
            f"/repos/{owner}/{repo}/contents/{path}",
            json_body={k: v for k, v in payload.items() if v is not None},
        )

    def create_repository_dispatch(
        self,
        owner: str,
        repo: str,
        event_type: str,
        client_payload: dict[str, Any] | None,
    ) -> Any:
        payload = {
            "event_type": event_type,
            "client_payload": client_payload or {},
        }
        return self._request("POST", f"/repos/{owner}/{repo}/dispatches", json_body=payload)

    def trigger_workflow_dispatch(
        self,
        owner: str,
        repo: str,
        workflow_id: str,
        ref: str,
        inputs: dict[str, Any] | None,
    ) -> Any:
        payload = {
            "ref": ref,
            "inputs": inputs or {},
        }
        return self._request(
            "POST",
            f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
            json_body=payload,
        )

    def list_workflow_runs(
        self,
        owner: str,
        repo: str,
        actor: str | None,
        branch: str | None,
        event: str | None,
        status: str | None,
        per_page: int,
        page: int,
    ) -> Any:
        params = {
            "actor": actor,
            "branch": branch,
            "event": event,
            "status": status,
            "per_page": per_page,
            "page": page,
        }
        return self._request(
            "GET",
            f"/repos/{owner}/{repo}/actions/runs",
            params={k: v for k, v in params.items() if v is not None},
        )

# Made with Bob
