select
    event_id,
    patient_id,
    procedure_id,
    robot_arm,
    step,
    force_newtons,
    velocity_mm_s,
    latency_ms,
    error_code,
    cast(timestamp as timestamp) as event_ts,
    cast(timestamp as date) as event_day
from {{ source('iceberg', 'surgical_events') }}
