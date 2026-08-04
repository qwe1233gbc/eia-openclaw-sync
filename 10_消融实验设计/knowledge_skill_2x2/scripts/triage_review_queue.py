#!/usr/bin/env python3
from governance_core import ensure_dirs, make_records, triage
ensure_dirs(); triage(make_records())
