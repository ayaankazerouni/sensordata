
-- Uses userId, projectId, and time for uniqueness.
-- Returns 576 rows in ~33 seconds.
select userId, projectId
from (
  select userId, projectId, `time`, count(*) as qty
  from cleaned
  group by userId, projectId, `time`
  having qty > 1
) i
group by userId, projectId;

-- Using userId, projectId, time, and Unit-Name for uniqueness.
-- Returns ___ rows in ~___ seconds.
select distinct userId, projectId
from (
  select userId, projectId, `time`, `Unit-Name`, count(*) as qty
  from cleaned
  group by userId, projectId, `time`, `Unit-Name`
  having qty > 1
) b;
