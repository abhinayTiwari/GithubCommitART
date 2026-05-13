# GitHub Commit ART

**[🎨 Live Preview → abhinayTiwari.github.io/GithubCommitART](https://abhinayTiwari.github.io/GithubCommitART/)**

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

---

## Quickstart — no local setup needed

> **Design, preview, and draw — entirely inside GitHub's browser UI.**

1. Click **"Use this template"** on this repo to create your own private copy.
2. In your new repo go to **Settings → Actions → General → Workflow permissions** and select **Read and write permissions**.
3. Open the **live preview page** (GitHub Pages — see below), type your text, pick a Sunday start date, and see the contribution graph render in real time.
4. Go to **Actions → Draw Commit Art → Run workflow**, fill in the same values, and click **Run workflow**.
5. Wait ~10 minutes — GitHub processes the backdated commits and your profile graph updates automatically.

---

## Live preview

The `docs/` folder is a zero-dependency static site. Enable it once in your repo:

**Settings → Pages → Source: Deploy from branch → `master` → `/docs`**

After GitHub publishes it (usually under a minute), visit:

```
https://<your-username>.github.io/GithubCommitART/
```

The page lets you:
- Type your word and see the contribution grid render live as you type
- Auto-snap to the next Sunday with one button
- See the exact date range and total active-day count
- Jump directly to the Actions workflow pre-loaded with your values

---

## GitHub Actions workflow

The workflow at `.github/workflows/draw-commit-art.yml` is triggered manually via `workflow_dispatch`. It presents a form with these fields:

| Field | Required | Description |
|---|---|---|
| Text to draw | ✓ | A–Z, 0–9, symbols like `@ ! # $ % & * + - . ? _` |
| Start date | ✓ | `YYYY-MM-DD` — **must be a Sunday** |
| Your display name | ✓ | Exactly as shown on your GitHub profile |
| Your verified email | ✓ | Must be a verified email on your GitHub account |
| Commits per day | | `1–20`, default `20` (darkest green) |
| Letter spacing | | Empty columns between letters, default `2` |
| Word spacing | | Empty columns between words, default `4` |
| Dry run | | Preview only — prints the grid, creates no commits |

No personal access tokens or secrets are required. The workflow uses the built-in `GITHUB_TOKEN`.

---

## How it works

The contribution graph is a 7-row × 52-week grid. This tool maps a pixel-font onto that grid and creates backdated git commits using `GIT_AUTHOR_DATE` / `GIT_COMMITTER_DATE` — a standard git feature. Push once and GitHub renders the art on your profile.

- **Past dates** appear immediately after pushing.
- **Future dates** appear as each day arrives.
- No third-party packages — pure Python standard library.

---

## Local CLI usage

If you prefer to run the tool locally:

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

# Skip confirmation prompt (useful in scripts)
py main.py --word "WORKS @ NASA" --start-date 2025-02-16 --yes
```

> **Start date must be a Sunday.** This aligns the first column with the top of the contribution calendar.

### Requirements

- Python 3.x
- Git installed and configured
- A GitHub repo with your verified email attached

### Options

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
| `--yes` | — | Skip the confirmation prompt (for scripts / CI) |

### Configuration

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

---

## File structure

```
GithubCommitART/
├── .github/
│   └── workflows/
│       └── draw-commit-art.yml   # GitHub Actions — draw from the browser UI
├── docs/
│   └── index.html                # GitHub Pages live preview site
├── main.py                       # CLI entry point
├── config.py                     # Settings and pixel font (A–Z, 0–9, symbols)
├── calendar_mapper.py            # Maps letters → calendar dates
├── commit_generator.py           # Creates backdated git commits
└── commit_log.txt                # Auto-created; modified by each commit
```

---

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
GitHub only credits commits to your profile when the commit author email is connected to your account and the commits land on the default branch. Make sure the email you enter (in the Actions form or via `--author-email`) is listed as a verified email in your GitHub account settings.
