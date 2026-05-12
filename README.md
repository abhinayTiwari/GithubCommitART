# GitHub Commit ART

Draw pixel-art text on your GitHub contribution graph using backdated git commits. Each "lit" cell on the calendar receives 20 commits, producing the darkest green color. Empty cells stay grey, creating a readable contrast that forms the letters.

```
Sun  #...#...###....###....###...
Mon  ##..#..#...#..#...#..#...#..
Tue  #.#.#..#...#..#......#...#..
Wed  #.#.#..#####...###...#####..
Thu  #..##..#...#......#..#...#..
Fri  #...#..#...#..#...#..#...#..
Sat  #...#..#...#...###...#...#..
```

## How it works

The GitHub contribution graph is a 7-row grid (Sunday→Saturday) that spans 52 weeks left to right. This tool maps pixel-font letters onto that grid and creates backdated git commits using git's built-in `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` environment variables — a standard git feature. When pushed to GitHub, the contribution graph renders the commits on their authored date, drawing the text.

- Past dates appear immediately on your graph after pushing.
- Future dates appear on your graph as each day arrives.
- Your other repos and projects are completely unaffected.

## Requirements

- Python 3.x (Windows: use `py`, macOS/Linux: use `python3`)
- Git installed and configured
- A GitHub account with a connected remote repo

No third-party packages required — pure Python standard library only.

## Quick start

```powershell
# 1. Clone or download this repo
git clone https://github.com/abhinayTiwari/GithubCommitART.git
cd GithubCommitART

# 2. Preview what will be drawn (no commits written)
py main.py --start-date 2026-01-04 --word NASA --dry-run

# 3. Generate the commits
py main.py --start-date 2026-01-04 --word NASA

# 4. Push to GitHub
git push
```

## Choosing a start date

The start date **must be a Sunday** — this ensures the first pixel column aligns with the top of the contribution calendar grid. The tool will warn you if you pick a non-Sunday.

To find the next Sunday from any date, check a calendar or run:

```powershell
py -c "from datetime import date, timedelta; d=date(2026,1,4); print(d + timedelta(days=(6-d.weekday())%7))"
```

## Options

| Flag | Default | Description |
|---|---|---|
| `--word` | `NASA` | Word to draw — uppercase A-Z and spaces only |
| `--start-date` | `2026-05-03` | Start date — **must be a Sunday** |
| `--commits` | `20` | Commits per active day (20 = darkest green) |
| `--letter-spacing` | `2` | Empty columns between letters |
| `--word-spacing` | `4` | Empty columns for a space between words |
| `--repo-path` | `.` | Path to the target git repo |
| `--author-name` | current git config | Explicit author name for generated commits |
| `--author-email` | current git config | Explicit author email for generated commits |
| `--dry-run` | — | Preview only, no commits written |

## Customization

Change the defaults permanently in `config.py`:

```python
WORD            = "NASA"        # Word to draw
START_DATE      = date(2026, 1, 4)
COMMITS_PER_DAY = 20            # 20 = darkest green on GitHub
LETTER_WIDTH    = 5             # Columns per letter (wider = clearer)
LETTER_SPACING  = 2             # Empty cols between letters
WORD_SPACING    = 4             # Empty cols between words
AUTHOR_NAME     = None          # Optional explicit author name for generated commits
AUTHOR_EMAIL    = None          # Optional explicit author email (must be verified on GitHub)
```

You can also add or modify letter pixel patterns in the `LETTERS` dictionary inside `config.py`. Each letter is a 7-row × 5-column grid where `1` means commit and `0` means no commit.

## File structure

```
GithubCommitART/
├── main.py               # CLI entry point
├── config.py             # Settings and A-Z pixel font definitions
├── calendar_mapper.py    # Maps letters to calendar dates
├── commit_generator.py   # Creates backdated git commits
├── requirements.txt      # No external dependencies
└── commit_log.txt        # Auto-created; the file modified by each commit
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
