# GitHub Commit ART

Draw pixel-art text on your GitHub contribution graph using backdated git commits.

```
Sun  #...#...###....###....###...
Mon  ##..#..#...#..#...#..#...#..
Tue  #.#.#..#...#..#......#...#..
Wed  #.#.#..#####...###...#####..
Thu  #..##..#...#......#..#...#..
Fri  #...#..#...#..#...#..#...#..
Sat  #...#..#...#...###...#...#..
```

Each "lit" cell gets 20 commits (darkest green). Empty cells stay grey, forming the letters.

## How it works

The contribution graph is a 7-row × 52-week grid. This tool maps a pixel-font onto that grid and creates backdated git commits using `GIT_AUTHOR_DATE` / `GIT_COMMITTER_DATE` — a standard git feature. Push once and GitHub renders the art on your profile.

- **Past dates** appear immediately after pushing.
- **Future dates** appear as each day arrives.
- No third-party packages — pure Python standard library.

## Requirements

- Python 3.x
- Git installed and configured
- A GitHub repo with your verified email attached

## Usage

**Interactive mode** — just run with no arguments:

```powershell
py main.py
```

You'll be prompted for the text, start date, and shown a preview before anything is written.

**CLI mode:**

```powershell
# Preview only (no commits written)
py main.py --word "WORKS @ NASA" --start-date 2025-02-16 --dry-run

# Generate and auto-push
py main.py --word "WORKS @ NASA" --start-date 2025-02-16

# Generate without pushing
py main.py --word "WORKS @ NASA" --start-date 2025-02-16 --no-push
```

> **Start date must be a Sunday.** This aligns the first column with the top of the contribution calendar.

## Options

| Flag | Default | Description |
|---|---|---|
| `--word` | `NASA` | Text to draw (A–Z, 0–9, most punctuation) |
| `--start-date` | config value | Start date — **must be a Sunday** |
| `--commits` | `20` | Commits per active day (20 = darkest green) |
| `--letter-spacing` | `2` | Empty columns between letters |
| `--word-spacing` | `4` | Empty columns between words |
| `--repo-path` | `.` | Path to the target git repo |
| `--author-name` | git config | Override commit author name |
| `--author-email` | git config | Override commit author email (must be GitHub-verified) |
| `--dry-run` | — | Preview only, no commits written |
| `--no-push` | — | Generate commits but skip the push |

## Configuration

Edit `config.py` to change defaults:

```python
WORD            = "NASA"
START_DATE      = date(2026, 1, 4)
COMMITS_PER_DAY = 20        # 20 = darkest green
LETTER_WIDTH    = 5
LETTER_SPACING  = 2
WORD_SPACING    = 4
AUTHOR_NAME     = None      # falls back to git config
AUTHOR_EMAIL    = None      # must be a GitHub-verified email
```

## File structure

```
GithubCommitART/
├── main.py               # CLI entry point
├── config.py             # Settings and pixel font (A–Z, 0–9, symbols)
├── calendar_mapper.py    # Maps letters → calendar dates
├── commit_generator.py   # Creates backdated git commits
└── commit_log.txt        # Auto-created; modified by each commit
```

## FAQ

**Will this get my account banned?**
No. Git backdating uses official git features (`GIT_AUTHOR_DATE`). GitHub does not prohibit commit art. It has been a popular community practice for over a decade.

**Will it overwrite my existing contributions?**
No. Commits are additive. If you already have commits on a planned date, the total count for that day increases. Your existing repos and history are not modified.

**Can I draw multiple words?**
Yes — pass a phrase with spaces: `--word "HI WORLD"`. Each space becomes 4 empty columns between the words.

**What if a letter looks wrong in the preview?**
Widen the terminal window so all columns fit on one line. The preview uses `#` for active days and `.` for empty days.

**I can see the commits in the repo, but not on my contribution graph. Why?**
GitHub only credits commits to your profile when the commit author email is connected to your account and the commits land on the default branch (or `gh-pages`). By default, this tool uses your current git-configured author identity. If that email is wrong, pass `--author-email your-verified-email@example.com` or set `AUTHOR_EMAIL` in `config.py` before generating commits.
