"""Partitions split an asset into independently materializable slices.

One partition per day: re-running 2026-10-05 only recomputes that day, and
"backfill the last month" is a button in the UI.
"""

import dagster as dg

START_DATE = "2026-10-01"

# The last partition is YESTERDAY: a day's partition only exists once the day
# is complete (end_offset=1 would include today's still-open day).
daily = dg.DailyPartitionsDefinition(start_date=START_DATE)
