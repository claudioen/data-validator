import yaml
import pandas as pd
from validator.core import validate_data

def test_basic_validation():
    # Minimal inline dataset
    df = pd.DataFrame({
        "user_id": [1, 2, 2],
        "age": [10, None, 200],
        "email": ["a@b.com", "bad@", "c@d.com"],
        "signup_date": ["2022-01-01", "2019-01-01", "2023-05-05"]
    })

    config = yaml.safe_load(r'''
rules:
  - column: user_id
    unique: true
  - column: age
    type: int
    min: 0
    max: 120
  - column: email
    regex: '^[^@\s]+@[^@\s]+\.[^@\s]+$'
  - column: signup_date
    type: date
    min: '2020-01-01'
''')


    results = validate_data(df, config)
    assert results["summary"]["validation_passed"] is False
    assert results["summary"]["rows_checked"] == 3
    assert results["summary"]["rows_failed"] >= 1
