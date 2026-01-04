# Plan: GitHub Commit Art — NASA in Contributions Calendar

**Status**: Implementation in progress - creating all required files

## TL;DR
Build a Python tool that strategically commits 20 times daily on selected dates to spell customizable words (default: "NASA") in GitHub's contributions calendar. The tool will:
1. Calculate which dates map to letter pixels (using a 5×3 grid per letter with 3-column spacing between letters)
2. Generate commits with timestamps starting May 3, 2026
3. Push all commits to a private repository to maximize green intensity

---

## Steps

### Phase 1: Setup & Foundation
1. **Initialize private Git repository** in the workspace
   - Repo name: `GithubCommitART` (already named in workspace)
   - Private GitHub repo linked locally

2. **Design letter pixel mapping** for customizable words
   - GitHub calendar: 7 rows (Mon-Sun), ~52 columns per year
   - Standard 5×3 pixel grid per letter (standard in pixel fonts)
   - **Spacing**: 3 empty columns between each letter; e.g., "NASA" = N(0-2) + gap(3-5) + A(6-8) + gap(9-11) + S(12-14) + gap(15-17) + A(18-20)
   - Create pixel definitions for all uppercase letters A-Z (5×3 bitmaps)
   - Calculate absolute dates for each pixel given May 3, 2026 = Week 0, Day 5 (Friday)
   - *Depends on Phase 1 completion*

3. **Create Python project structure**
   - `main.py` — orchestrate the workflow
   - `calendar_mapper.py` — convert letter pixels to dates
   - `commit_generator.py` — create dated commits
   - `config.py` — store constants (start date, commit count, letter definitions)
   - `requirements.txt` — dependencies (GitPython or similar)

### Phase 2: Implementation
4. **Implement calendar_mapper module**
   - Define 5×3 pixel grids for all uppercase letters A-Z
   - Accept customizable word from config (not hardcoded)
   - Apply 3-column spacing logic between each letter
   - Map pixels to absolute dates starting May 3, 2026
   - Validate no overlap between letters, handle month boundaries
   - Output: set of target dates with letter/word metadata

5. **Implement commit_generator module**
   - For each target date, create 20 commits with:
     - Commit message: `"Commit for YYYY-MM-DD [timestamp HH:MM:SS]"` (trackable & meaningful)
     - Author date & commit date set to target date (different times, 5–6 minutes apart)
   - Modify a simple tracking file (e.g., `log.txt` or `commits.md`) to append commit records
   - *Depends on Phase 2.1*

6. **Implement main.py workflow**
   - Load configuration (start date, **word/phrase to display**, commit count)
   - Call calendar_mapper to get target dates (handles spacing automatically)
   - Call commit_generator to stage and push commits
   - Handle Git operations (add, commit, push)
   - *Depends on Phase 2.1 & 2.2*

### Phase 3: Testing & Refinement
7. **Dry-run mode**
   - Run with `--dry-run` flag to print planned commits without pushing
   - Verify date calculation is correct (visualize calendar output)
   - Adjust pixel patterns if needed

8. **Execute commits** (with user approval)
   - Run tool with real Git operations
   - Validate commits appear on GitHub contributions calendar within 24–48 hours

---

## Relevant Files
- `main.py` — orchestrates commit generation and Git operations
- `calendar_mapper.py` — converts letter pixels to commit dates; uses reference calendars to map 5×7 grids to week/day offsets
- `commit_generator.py` — creates local commits with proper timestamps and trackable messages
- `config.py` — stores pixel patterns for all A-Z letters; start date (May 3, 2026); word to display (customizable, default "NASA"); commit count (20); spacing (3 columns)
- `.gitignore` — exclude virtual env, `__pycache__`, `.env`
- Private GitHub repository remote

---

## Verification
1. **Dry-run output check**: `python main.py --dry-run` shows:
   - All target dates for each letter pixel with spacing ✓
   - Visual ASCII calendar preview of the complete word/phrase
   - Total commit count validates against word length × pixels × commits
   - No date collisions

2. **Local Git history**: `git log --oneline | head -100` shows commits with correct timestamps

3. **GitHub validation** (24–48 hours after push):
   - Check GitHub contributions calendar; the configured word/phrase is visible in dark green
   - Verify private repo appears in contribution count

---

## Decisions & Assumptions
- **Start date**: May 3, 2026 (Friday) = Week 0, Row 5 (if weeks run left-to-right)
- **Pixel grid**: Standard 5×7 (5 rows, 3 columns per letter minimum); validated against GitHub's day-of-week layout
- **Spacing**: 3 empty columns between words for visual separation
- **Customizable word**: Config accepts any word/phrase; tool generates pixel patterns dynamically for all letters
- **Commit style**: Dummy commits with date/time in message for easy tracking; no meaningful code changes
- **Repository**: Private to keep it clean; commits still count toward GitHub contributions
- **Push strategy**: All commits pushed in one batch after generation (or can batch by letter if too large)
- **Timezone**: Commits use a consistent timezone (user's local TZ) to simplify logic

---

## Further Considerations
1. **GitHub API rate limits**: Private repo push of 1,000+ commits should be fine for single push; monitor if using GitHub API for validation
2. **File tracking**: `commits.md` or `log.txt` will grow significantly—acceptable for visual tracking, can be excluded from display if desired
3. **Customization**: Word length affects total column width needed. Verify start date leaves enough weeks to display the word (alphabet patterns + spacing)
