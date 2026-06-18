from typing import Any, Literal

from pydantic import BaseModel, Field


class OwnerRepoRequest(BaseModel):
    owner: str = Field(..., min_length=1, description="Repository owner or organization")
    repo: str = Field(..., min_length=1, description="Repository name")


class IssueIdentifierRequest(OwnerRepoRequest):
    issue_number: int = Field(..., ge=1, description="Issue number")


class PullRequestIdentifierRequest(OwnerRepoRequest):
    pull_number: int = Field(..., ge=1, description="Pull request number")


class BranchRequest(OwnerRepoRequest):
    branch: str = Field(..., min_length=1, description="Branch name")


class FileContentRequest(OwnerRepoRequest):
    path: str = Field(..., min_length=1, description="Repository file path")
    ref: str | None = Field(default=None, description="Git ref, branch, tag, or commit SHA")


class ListRepositoryFilesRequest(OwnerRepoRequest):
    path: str | None = Field(default=None, description="Optional directory path inside the repository")
    ref: str | None = Field(default=None, description="Git ref, branch, tag, or commit SHA")


class RepositoryDetailsRequest(OwnerRepoRequest):
    include_branches: bool = True
    include_root_files: bool = True
    include_readme: bool = False


class SearchRepositoriesRequest(BaseModel):
    query: str = Field(..., min_length=1, description="GitHub repository search query")
    sort: Literal["stars", "forks", "help-wanted-issues", "updated"] | None = None
    order: Literal["asc", "desc"] | None = None
    per_page: int = Field(default=10, ge=1, le=100)
    page: int = Field(default=1, ge=1)


class SearchCodeRequest(BaseModel):
    query: str = Field(..., min_length=1, description="GitHub code search query")
    sort: Literal["indexed"] | None = None
    order: Literal["asc", "desc"] | None = None
    per_page: int = Field(default=10, ge=1, le=100)
    page: int = Field(default=1, ge=1)


class SearchIssuesRequest(BaseModel):
    query: str = Field(..., min_length=1, description="GitHub issues or pull requests search query")
    sort: Literal["comments", "reactions", "reactions-+1", "reactions--1", "reactions-smile", "reactions-thinking_face", "reactions-heart", "reactions-tada", "interactions", "created", "updated"] | None = None
    order: Literal["asc", "desc"] | None = None
    per_page: int = Field(default=10, ge=1, le=100)
    page: int = Field(default=1, ge=1)


class CreateRepositoryRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Repository name")
    description: str | None = None
    homepage: str | None = None
    private: bool = True
    has_issues: bool = True
    has_projects: bool = True
    has_wiki: bool = True
    auto_init: bool = False
    gitignore_template: str | None = None
    license_template: str | None = None

class CreateIssueRequest(OwnerRepoRequest):
    title: str = Field(..., min_length=1)
    body: str | None = None
    assignees: list[str] | None = None
    labels: list[str] | None = None
    milestone: int | None = Field(default=None, ge=1)


class CreateCommentRequest(IssueIdentifierRequest):
    body: str = Field(..., min_length=1)


class UpdateIssueRequest(IssueIdentifierRequest):
    title: str | None = None
    body: str | None = None
    state: Literal["open", "closed"] | None = None
    state_reason: Literal["completed", "not_planned", "reopened"] | None = None
    assignees: list[str] | None = None
    labels: list[str] | None = None
    milestone: int | None = Field(default=None, ge=1)


class CreatePullRequestRequest(OwnerRepoRequest):
    title: str = Field(..., min_length=1)
    head: str = Field(..., min_length=1, description="The name of the branch where your changes are implemented")
    base: str = Field(..., min_length=1, description="The name of the branch you want the changes pulled into")
    body: str | None = None
    maintainer_can_modify: bool = True
    draft: bool = False


class MergePullRequestRequest(PullRequestIdentifierRequest):
    commit_title: str | None = None
    commit_message: str | None = None
    merge_method: Literal["merge", "squash", "rebase"] = "merge"


class CreateOrUpdateFileRequest(OwnerRepoRequest):
    path: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1, description="Raw file content; server base64-encodes it")
    branch: str | None = None
    sha: str | None = None
    committer: dict[str, str] | None = None
    author: dict[str, str] | None = None


class AppendToFileRequest(OwnerRepoRequest):
    path: str = Field(..., min_length=1, description="Repository file path")
    content: str = Field(..., min_length=1, description="Content to append to the file")
    message: str = Field(default="Append content to file", description="Commit message")
    branch: str | None = Field(default=None, description="Branch name (defaults to repository's default branch)")
    committer: dict[str, str] | None = None
    author: dict[str, str] | None = None


class DeleteFileRequest(OwnerRepoRequest):
    path: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    sha: str = Field(..., min_length=1)
    branch: str | None = None
    committer: dict[str, str] | None = None
    author: dict[str, str] | None = None


class CreateDispatchEventRequest(OwnerRepoRequest):
    event_type: str = Field(..., min_length=1)
    client_payload: dict[str, Any] | None = None


class TriggerWorkflowDispatchRequest(OwnerRepoRequest):
    workflow_id: str = Field(..., min_length=1, description="Workflow file name or workflow ID")
    ref: str = Field(..., min_length=1)
    inputs: dict[str, Any] | None = None


class ListWorkflowRunsRequest(OwnerRepoRequest):
    actor: str | None = None
    branch: str | None = None
    event: str | None = None
    status: str | None = None
    per_page: int = Field(default=10, ge=1, le=100)
    page: int = Field(default=1, ge=1)


class GetCommitRequest(OwnerRepoRequest):
    ref: str = Field(..., min_length=1, description="Commit SHA, branch, or tag")


class CompareCommitsRequest(OwnerRepoRequest):
    basehead: str = Field(..., min_length=3, description="Comparison specifier like main...feature-branch")


class InsertContentRequest(OwnerRepoRequest):
    """Insert new content at a specific line in a file without recreating it"""
    path: str = Field(..., min_length=1, description="File path in repository")
    line_number: int = Field(..., ge=1, description="Line number where content will be inserted (1-based)")
    content: str = Field(..., min_length=1, description="Content to insert at the specified line")
    message: str = Field(..., min_length=1, description="Commit message")
    branch: str | None = Field(default=None, description="Branch name (default: repository default branch)")
    committer: dict[str, str] | None = None
    author: dict[str, str] | None = None


class ReplaceContentRequest(OwnerRepoRequest):
    """Replace specific content in a file without recreating it"""
    path: str = Field(..., min_length=1, description="File path in repository")
    old_content: str = Field(..., min_length=1, description="Content to find and replace")
    new_content: str = Field(..., min_length=1, description="New content to replace with")
    message: str = Field(..., min_length=1, description="Commit message")
    branch: str | None = Field(default=None, description="Branch name (default: repository default branch)")
    replace_all: bool = Field(default=False, description="Replace all occurrences (default: false)")
    occurrence: int | None = Field(default=None, ge=1, description="Specific occurrence number to replace (1-based). If not set and replace_all=false, replaces first occurrence")
    committer: dict[str, str] | None = None
    author: dict[str, str] | None = None


class GenericGitHubResponse(BaseModel):
    ok: bool = True
    operation: str
    data: Any


class ToolDescriptor(BaseModel):
    name: str
    description: str
    rest_path: str
    method: Literal["POST"] = "POST"
    request_model: str


class ToolCatalogResponse(BaseModel):
    ok: bool = True
    tools: list[ToolDescriptor]

# Made with Bob
