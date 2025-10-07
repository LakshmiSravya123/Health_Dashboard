# Vercel serverless entrypoint for Dash (Flask WSGI app)
# Exposes `app` which Vercel will use as the WSGI handler.

import sys
from pathlib import Path

# Ensure project root is on path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.dashboard.app import MentalHealthDashboard

# Build Dash app but DO NOT run the server here
_dash = MentalHealthDashboard().app

# Vercel expects a WSGI app named `app`
app = _dash.server
