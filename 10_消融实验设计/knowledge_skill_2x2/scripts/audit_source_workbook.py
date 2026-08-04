#!/usr/bin/env python3
from governance_core import audit, ensure_dirs, make_records
ensure_dirs(); audit(make_records())
