#!/usr/bin/env python3
from governance_core import REPORTS, anomalies, ensure_dirs, make_records, write_csv
ensure_dirs(); write_csv(REPORTS / "judgement_anomalies.csv", anomalies(make_records()))
