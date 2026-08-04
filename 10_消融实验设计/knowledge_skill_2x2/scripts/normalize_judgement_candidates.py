#!/usr/bin/env python3
from governance_core import ensure_dirs, export, make_records
ensure_dirs(); export(make_records())
