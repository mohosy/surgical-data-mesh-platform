with base as (
    select * from {{ ref('stg_surgical_events') }}
)

select
    event_day,
    patient_id,
    procedure_id,
    count(*) as events,
    sum(case when force_newtons >= 40 or latency_ms >= 150 then 1 else 0 end) as high_risk_events,
    max(force_newtons) as max_force_newtons,
    avg(latency_ms) as avg_latency_ms
from base
group by 1,2,3
