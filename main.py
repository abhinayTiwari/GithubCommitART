"""
main.py — GitHub Commit Art

Usage examples:
  python main.py --dry-run                    # preview default word "NASA"
  python main.py --dry-run --word HELLO       # preview a different word
  python main.py                              # generate commits for "NASA"
  python main.py --word HELLO --commits 15   # custom word, 15 commits/day
  python main.py --start-date 2026-06-01     # different start date (must be Sunday)

Flags:
  --word TEXT          Word to spell (default from config.py: NASA)
  --start-date DATE    Start date in YYYY-MM-DD format; must be a Sunday
  --commits N          Commits per active day (default 20)
  --spacing N          Empty columns between letters (default 3)
  --repo-path PATH     Path to git repo (default: current directory)
  --dry-run            Show planned commits without writing anything
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


def main() -> None:
    args = _build_parser().parse_args()

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
        print("  Supported characters: A-Z and spaces.")
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
    print(f"  Repository    : {repo_path}")
    print()
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
    print("  Next: run  git push  to send them to GitHub.")
    print("  Your contributions calendar should update within 24–48 hours.")


if __name__ == "__main__":
    main()
