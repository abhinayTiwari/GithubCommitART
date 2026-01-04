"""
calendar_mapper.py

Converts a word into a mapping of {date: label} by projecting
each letter's 7x3 pixel grid onto GitHub's contributions calendar.

GitHub contributions grid layout:
  - Columns = weeks (left to right)
  - Rows    = days of week (row 0 = Sunday, row 6 = Saturday)
  - start_date must be a Sunday (row 0 of week column 0)

Spacing rules:
  - LETTER_SPACING: empty columns inserted between consecutive letters.
  - WORD_SPACING:   columns consumed by a space character between words.
"""
from datetime import date, timedelta
from typing import Dict, List, Tuple

import config


# Day-of-week labels matching GitHub's grid (row 0 = Sunday)
_DAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def _col_offsets(
    word: str,
    letter_width: int,
    letter_spacing: int,
    word_spacing: int,
) -> List[Tuple[str, int]]:
    """
    Returns [(char, col_offset), ...] for every character in word.
    Letters advance cursor by letter_width + letter_spacing.
    Spaces advance cursor by word_spacing (no pixel placed).
    """
    offsets: List[Tuple[str, int]] = []
    cursor = 0
    for char in word.upper():
        offsets.append((char, cursor))
        if char == " ":
            cursor += word_spacing
        else:
            cursor += letter_width + letter_spacing
    return offsets


def word_to_commit_dates(
    word: str,
    start_date: date,
    letter_width: int = None,
    letter_spacing: int = None,
    word_spacing: int = None,
) -> Dict[date, str]:
    """
    Maps each lit pixel of `word` to a calendar date.

    - letter_spacing: empty columns between consecutive letters.
    - word_spacing:   columns consumed by a space character between words.

    Returns a dict mapping each target date to a label like "N[row=2,col=1]".
    """
    if letter_width is None:
        letter_width = config.LETTER_WIDTH
    if letter_spacing is None:
        letter_spacing = config.LETTER_SPACING
    if word_spacing is None:
        word_spacing = config.WORD_SPACING

    commit_dates: Dict[date, str] = {}

    for char, col_offset in _col_offsets(word, letter_width, letter_spacing, word_spacing):
        if char == " ":
            continue
        if char not in config.LETTERS:
            print(f"  [Warning] '{char}' has no pixel pattern -- skipped.")
            continue

        letter_grid = config.LETTERS[char]
        for row_index, row in enumerate(letter_grid):
            for pixel_col, pixel in enumerate(row):
                if pixel == 1:
                    week_col = col_offset + pixel_col
                    day_offset = week_col * 7 + row_index
                    target_date = start_date + timedelta(days=day_offset)
                    label = f"{char}[row={row_index},col={pixel_col}]"
                    commit_dates[target_date] = label

    return commit_dates


def get_total_weeks(
    word: str,
    letter_width: int = None,
    letter_spacing: int = None,
    word_spacing: int = None,
) -> int:
    """Returns the total number of calendar columns (weeks) the word spans."""
    if letter_width is None:
        letter_width = config.LETTER_WIDTH
    if letter_spacing is None:
        letter_spacing = config.LETTER_SPACING
    if word_spacing is None:
        word_spacing = config.WORD_SPACING
    total = 0
    for char in word.upper():
        total += word_spacing if char == " " else letter_width + letter_spacing
    return total


def preview_calendar(
    word: str,
    start_date: date,
    letter_width: int = None,
    letter_spacing: int = None,
    word_spacing: int = None,
) -> None:
    """Prints an ASCII art preview of the commit pattern on a 7-row calendar grid."""
    if letter_width is None:
        letter_width = config.LETTER_WIDTH
    if letter_spacing is None:
        letter_spacing = config.LETTER_SPACING
    if word_spacing is None:
        word_spacing = config.WORD_SPACING

    total_cols = get_total_weeks(word, letter_width, letter_spacing, word_spacing)

    # Build a 7 x total_cols grid
    grid = [["."] * total_cols for _ in range(7)]

    for char, col_offset in _col_offsets(word, letter_width, letter_spacing, word_spacing):
        if char == " " or char not in config.LETTERS:
            continue
        letter_grid = config.LETTERS[char]
        for row_index, row in enumerate(letter_grid):
            for pixel_col, pixel in enumerate(row):
                if pixel == 1:
                    grid[row_index][col_offset + pixel_col] = "#"

    commits_per_day = config.COMMITS_PER_DAY
    print(f"\n  Preview: '{word}'  (start: {start_date}  |  '#' = {commits_per_day} commits/day)")
    print()
    for row_index in range(7):
        label = _DAY_LABELS[row_index]
        print(f"  {label}  {''.join(grid[row_index])}")
    print()

    # Column week-number ruler
    ruler = "".join(str(c % 10) if c % 5 == 0 else " " for c in range(total_cols))
    print(f"  wk#  {ruler}")
    print()
