---
name: csv-column-stats
description: Compute summary statistics (count, mean, min, max) for a named column in a CSV file. Use when the user asks for stats, an average, or a summary of a CSV column.
---

# CSV Column Stats

Given a CSV path and a column name, print the count, mean, min, and max for that column.

- Treat the first row as headers.
- Skip rows where the target cell is empty, and report how many rows were skipped.
- Round the mean to 2 decimal places.
