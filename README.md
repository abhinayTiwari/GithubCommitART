# GitHub Commit ART

Generates backdated git commits to draw pixel-art text on the GitHub contribution graph.

## Usage

```powershell
py main.py --start-date 2026-01-04 --word NASA
```

## Options

| Flag | Default | Description |
|---|---|---|
| `--word` | `NASA` | Word to draw (A-Z only) |
| `--start-date` | `2026-05-03` | Start date — **must be a Sunday** |
| `--commits` | `20` | Commits per active day (20 = darkest green) |
| `--letter-spacing` | `2` | Empty columns between letters |
| `--word-spacing` | `4` | Empty columns between words |
| `--repo-path` | `.` | Path to the git repo |
| `--dry-run` | — | Preview only, no commits written |

## Workflow

```powershell
# 1. Preview
py main.py --start-date 2026-01-04 --word NASA --dry-run

# 2. Generate commits
py main.py --start-date 2026-01-04 --word NASA

# 3. Push to GitHub
git push
```
