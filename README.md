# Baseliner Client

### Building Instructions
```bash
git clone https://github.com/JayjeetAtGithub/baseliner-py
cd baseliner-py/
pip install .
```

### Example Usage:

```python3
from baseliner import Baseliner

baseliner = Baseliner()
baseliner.connect('<user>', '<passwd>', '<db>', '<hostname>')
baseliner.set_allowed_err_and_trial_cnt(0.05, 200)

print(baseliner.get_num_reps(
    machine_predicate={
        "architecture": "amd64"
    },
    benchmark_predicate={
    }, param='READ_IOPS', test='fio'))
```

Look into `usage/` for more example usage.
