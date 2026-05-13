"""
main.py — GitHub Commit Art

Run with no arguments for interactive mode (recommended):
  python main.py

Or use flags directly:
  python main.py --dry-run                       # preview default word
  python main.py --word "HELLO WORLD" --dry-run  # preview a custom phrase
  python main.py --word "HI" --start-date 2026-01-04  # generate + push

Flags:
  --word TEXT          Text to spell (A-Z, 0-9, symbols; default from config.py)
  --start-date DATE    Start date YYYY-MM-DD; must be a Sunday
  --commits N          Commits per active day (default 20)
  --letter-spacing N   Empty columns between letters (default 2)
  --word-spacing N     Columns for a space between words (default 4)
  --repo-path PATH     Path to git repo (default: current directory)
  --author-name TEXT   Override git author name
  --author-email EMAIL Override git author email (must be verified on GitHub)
  --no-push            Skip the automatic git push after generating commits
  --dry-run            Preview commit pattern without writing anything
"""
import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

import config
from calendar_mapper import word_to_commit_dates, preview_calendar, get_total_weeks
from commit_generator import generate_commits


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date '{value}'. Expected YYYY-MM-DD."
        ) from exc


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Spell a word in your GitHub contributions calendar via backdated commits.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--word",
        type=str,
        default=config.WORD,
        metavar="TEXT",
        help=f"Word to display (default: '{config.WORD}'). Supports A-Z and spaces.",
    )
    parser.add_argument(
        "--start-date",
        type=_parse_date,
        default=config.START_DATE,
        metavar="YYYY-MM-DD",
        help=f"Calendar start date — must be a Sunday (default: {config.START_DATE}).",
    )
    parser.add_argument(
        "--commits",
        type=int,
        default=config.COMMITS_PER_DAY,
        metavar="N",
        help=f"Commits per active day (default: {config.COMMITS_PER_DAY}). 10+ = darkest green.",
    )
    parser.add_argument(
        "--letter-spacing",
        type=int,
        default=config.LETTER_SPACING,
        metavar="N",
        help=f"Empty columns between consecutive letters (default: {config.LETTER_SPACING}).",
    )
    parser.add_argument(
        "--word-spacing",
        type=int,
        default=config.WORD_SPACING,
        metavar="N",
        help=f"Columns consumed by a space character between words (default: {config.WORD_SPACING}).",
    )
    parser.add_argument(
        "--repo-path",
        type=str,
        default=".",
        metavar="PATH",
        help="Path to the local git repository (default: current directory).",
    )
    parser.add_argument(
        "--author-name",
        type=str,
        default=config.AUTHOR_NAME,
        metavar="TEXT",
        help="Explicit git author name for generated commits (default: current git config).",
    )
    parser.add_argument(
        "--author-email",
        type=str,
        default=config.AUTHOR_EMAIL,
        metavar="EMAIL",
        help="Explicit git author email for generated commits (default: current git config). Must be verified on GitHub.",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Skip the automatic git push after generating commits.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the commit pattern without creating any commits.",
    )
    return parser


def _get_git_identity(repo_path: str) -> tuple[str | None, str | None]:
    def _read(key: str) -> str | None:
        result = subprocess.run(
            ["git", "config", key],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False,
        )
        value = result.stdout.strip()
        return value or None

    return _read("user.name"), _read("user.email")


def _supported_chars_hint() -> str:
    specials = sorted(k for k in config.LETTERS if not k.isalpha())
    return f"A-Z, 0-9, and: {'  '.join(specials)}"


def _interactive_prompt() -> tuple[str, date]:
    """Ask the user for the text and start date interactively."""
    print()
    print("  GitHub Commit Art — Interactive Setup")
    print(f"  Supported characters: {_supported_chars_hint()}")
    print()

    while True:
        raw_word = input("  Text to display: ").strip()
        if not raw_word:
            print("  Text cannot be empty.")
            continue
        missing = [ch for ch in raw_word.upper() if ch != " " and ch not in config.LETTERS]
        if missing:
            print(f"  Unsupported characters: {sorted(set(missing))}")
            print(f"  Supported: {_supported_chars_hint()}")
            continue
        break

    print()
    while True:
        raw_date = input("  Start date (YYYY-MM-DD, must be a Sunday): ").strip()
        try:
            d = date.fromisoformat(raw_date)
        except ValueError:
            print("  Invalid format. Use YYYY-MM-DD (e.g. 2026-01-04).")
            continue
        if d.weekday() != 6:
            print(f"  {d} is a {d.strftime('%A')}, not a Sunday. Please pick a Sunday.")
            continue
        break

    print()
    return raw_word, d


def _current_branch(repo_path: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() or "master"


def _git_push(repo_path: str) -> None:
    branch = _current_branch(repo_path)
    print(f"  Pushing to GitHub (origin/{branch})…")
    result = subprocess.run(
        ["git", "push", "origin", branch],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )
    output = (result.stdout + result.stderr).strip()
    if output:
        for line in output.splitlines():
            print(f"    {line}")
    if result.returncode == 0:
        print("  Pushed successfully! GitHub will update within 10–15 minutes.")
    else:
        print(f"  [Warning] Push failed. Run manually: git push origin {branch}")


def main() -> None:
    interactive = len(sys.argv) == 1
    args = _build_parser().parse_args()

    if interactive:
        word, start_date = _interactive_prompt()
        word = word.upper()
    else:
        word = args.word.upper()
        start_date: date = args.start_date
    commits_per_day: int = args.commits
    letter_spacing: int = args.letter_spacing
    word_spacing: int = args.word_spacing
    repo_path = str(Path(args.repo_path).resolve())
    author_name: str | None = args.author_name
    author_email: str | None = args.author_email
    git_name, git_email = _get_git_identity(repo_path)
    effective_author_name = author_name or git_name
    effective_author_email = author_email or git_email

    # ── Validate unsupported characters ──────────────────────────────────────
    missing = [ch for ch in word if ch != " " and ch not in config.LETTERS]
    if missing:
        unique = sorted(set(missing))
        print(f"  [Error] Unsupported characters: {unique}")
        print(f"  Supported: {_supported_chars_hint()}")
        sys.exit(1)

    # ── Warn if start date is not a Sunday ────────────────────────────────────
    if start_date.weekday() != 6:  # Python: Monday=0 … Sunday=6
        day_name = start_date.strftime("%A")
        print(f"  [Warning] {start_date} is a {day_name}, not a Sunday.")
        print("  GitHub's calendar starts each column on Sunday.")
        print("  The art may appear shifted by one or more rows.")
        print()

    # ── Compute target dates ──────────────────────────────────────────────────
    commit_dates = word_to_commit_dates(
        word,
        start_date,
        letter_width=config.LETTER_WIDTH,
        letter_spacing=letter_spacing,
        word_spacing=word_spacing,
    )

    if not commit_dates:
        print("  No commit dates generated. Check your word or configuration.")
        sys.exit(1)

    total_weeks = get_total_weeks(word, config.LETTER_WIDTH, letter_spacing, word_spacing)
    end_date = max(commit_dates.keys())
    total_commits = len(commit_dates) * commits_per_day

    # ── ASCII preview ─────────────────────────────────────────────────────────
    preview_calendar(word, start_date, config.LETTER_WIDTH, letter_spacing, word_spacing)

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"  Word          : '{word}'")
    print(f"  Start date    : {start_date}  ({start_date.strftime('%A')})")
    print(f"  End date      : {end_date}    ({end_date.strftime('%A')})")
    print(f"  Calendar span : ~{total_weeks} weeks")
    print(f"  Active days   : {len(commit_dates)}")
    print(f"  Commits/day   : {commits_per_day}")
    print(f"  Total commits : {total_commits}")
    print(f"  Author name   : {effective_author_name or '[not set]'}")
    print(f"  Author email  : {effective_author_email or '[not set]'}")
    if not author_email:
        print("  Note          : Using your current git-configured email for commit attribution.")
        print("                 Set --author-email or config.AUTHOR_EMAIL to a GitHub-verified email.")
    print()

    # ── Dry-run mode ──────────────────────────────────────────────────────────
    if args.dry_run:
        print("  [DRY RUN] Planned commit dates:")
        print()
        for d in sorted(commit_dates.keys()):
            print(f"    {d}  {d.strftime('%A'):<9}  {commit_dates[d]}")
        print()
        print(f"  [DRY RUN] {total_commits} commits would be created. Nothing written.")
        return

    # ── Confirm before writing ────────────────────────────────────────────────
    # In interactive mode the preview was already shown above; ask if they want
    # to proceed or restart. In CLI mode just show the repository and confirm.
    print(f"  Repository    : {repo_path}")
    print()
    if interactive:
        try:
            confirm = input("  Looks good? Proceed with generating commits? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n  Aborted.")
            sys.exit(0)
    else:
        try:
            confirm = input("  This will create commits with backdated timestamps. Proceed? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n  Aborted.")
            sys.exit(0)

    if confirm != "y":
        print("  Aborted.")
        sys.exit(0)

    print()

    # ── Generate commits ──────────────────────────────────────────────────────
    generate_commits(
        commit_dates=commit_dates,
        commits_per_day=commits_per_day,
        repo_path=repo_path,
        author_name=author_name,
        author_email=author_email,
        verbose=True,
    )

    print()
    print("  All commits created successfully!")
    print()

    # ── Push to GitHub ────────────────────────────────────────────────────────
    if not args.no_push:
        _git_push(repo_path)
    else:
        print("  Skipping push (--no-push). Run: git push origin master")


if __name__ == "__main__":
    main()
