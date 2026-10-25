"""
Git operations helper using dulwich for repository management and commit logging.
"""
import os
import dulwich.repo
import dulwich.porcelain

REPO_PATH = os.path.abspath(os.path.dirname(__file__))

def get_repo():
    return dulwich.repo.Repo(REPO_PATH)

def stage_and_commit(message: str, author: str = "FamilyCare AI Team <dev@familycare.ai>") -> str:
    """Stage all modified/new files and create a commit."""
    repo = get_repo()
    dulwich.porcelain.add(repo, paths=[REPO_PATH])
    commit_obj = dulwich.porcelain.commit(
        repo,
        message=message.encode("utf-8"),
        author=author.encode("utf-8")
    )
    commit_id = commit_obj.decode("ascii") if isinstance(commit_obj, bytes) else str(commit_obj)
    print(f"Committed: {commit_id[:8]} - {message}")
    return commit_id

def print_log(max_entries: int = 10):
    repo = get_repo()
    print("\n=== Git Commit History ===")
    walker = repo.get_walker(max_entries=max_entries)
    for entry in walker:
        commit = entry.commit
        msg = commit.message.decode("utf-8").strip()
        author = commit.author.decode("utf-8")
        cid = commit.id.decode("ascii")[:8]
        print(f"[{cid}] {msg} ({author})")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        stage_and_commit(" ".join(sys.argv[1:]))
    else:
        print_log()
