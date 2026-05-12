"""
commit_generator.py

Creates backdated git commits for every target date produced by calendar_mapper.
Each date receives `commits_per_day` commits, spread evenly across 24 hours.

Backdating is achieved by setting both GIT_AUTHOR_DATE and GIT_COMMITTER_DATE
environment variables before calling `git commit`.
"""
import os
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict


def _run_git(args: list, cwd: str, env: dict = None) -> None:
    """Run a git subcommand, raising on failure."""
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed:\n"
            f"  stdout: {result.stdout.strip()}\n"
            f"  stderr: {result.stderr.strip()}"
        )


def generate_commits(
    commit_dates: Dict[date, str],
    commits_per_day: int,
    repo_path: str,
    log_file: str = "commit_log.txt",
    author_name: str | None = None,
    author_email: str | None = None,
    verbose: bool = True,
) -> None:
    """
    For every date in `commit_dates`, create `commits_per_day` backdated git commits.

    Each commit:
      - Appends one line to `log_file` (the tracked file that changes per commit)
      - Has GIT_AUTHOR_DATE = GIT_COMMITTER_DATE = the target timestamp
      - Message: "Commit for YYYY-MM-DD HH:MM:SS [letter label]"

    Commits are spaced evenly across the day (86400 / commits_per_day seconds apart).
    """
    repo_path = str(Path(repo_path).resolve())
    log_path = Path(repo_path) / log_file

    # Ensure the log file exists so `git add` works from the first commit
    log_path.touch(exist_ok=True)

    sorted_dates = sorted(commit_dates.keys())
    total = len(sorted_dates) * commits_per_day
    done = 0

    # Seconds between consecutive commits within the same day
    interval_seconds = max(1, 86400 // commits_per_day)

    if verbose:
        print(f"  Generating {total} commits across {len(sorted_dates)} dates…")

    for target_date in sorted_dates:
        label = commit_dates[target_date]

        for commit_index in range(commits_per_day):
            # Distribute commits evenly: 00:00 → 23:xx
            commit_time = datetime.combine(
                target_date, datetime.min.time()
            ) + timedelta(seconds=commit_index * interval_seconds)

            iso_ts = commit_time.strftime("%Y-%m-%dT%H:%M:%S")

            # Modify the tracked log file
            log_entry = (
                f"{iso_ts} | {label} | commit {commit_index + 1}/{commits_per_day}\n"
            )
            with open(log_path, "a", encoding="utf-8") as fh:
                fh.write(log_entry)

            # Stage
            _run_git(["add", log_file], cwd=repo_path)

            # Commit with backdated timestamps
            message = f"Commit for {iso_ts} [{label}]"
            env = os.environ.copy()
            env["GIT_AUTHOR_DATE"] = iso_ts
            env["GIT_COMMITTER_DATE"] = iso_ts
            if author_name:
                env["GIT_AUTHOR_NAME"] = author_name
                env["GIT_COMMITTER_NAME"] = author_name
            if author_email:
                env["GIT_AUTHOR_EMAIL"] = author_email
                env["GIT_COMMITTER_EMAIL"] = author_email
            _run_git(["commit", "-m", message], cwd=repo_path, env=env)

            done += 1
            if verbose and done % 50 == 0:
                pct = done * 100 // total
                print(f"  Progress: {done}/{total} ({pct}%)")

    if verbose:
        print(f"  Done! {total} commits created.")
