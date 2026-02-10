# Profile Schema

Stored at `.weco/profile.yaml` (created silently, user can edit if desired):

```yaml
user:
  expertise: intermediate
  background: ml_engineer
  domain: fintech
  prefers_explanations: true

environment:
  os: darwin
  cpu: "Apple M2 Pro"
  cores: 10
  ram_gb: 16
  gpu: null

# For impact calculations
usage:
  calls_per_day: 50000
  compute_cost_per_hour: 3.50  # USD

constraints:
  - "no external dependencies"
  - "maintain API compatibility"

acceptable_tradeoffs:
  - "increased memory OK"

unacceptable_tradeoffs:
  - "no accuracy loss"

optimization_history:
  - task: model_forward
    file: src/model.py
    metric: speedup
    baseline_value: 847
    achieved_value: 187
    improvement: 4.5x
    monthly_savings: "$1,980"
    date: 2024-01-15
    approach: "GPU offload with cupy"
```
