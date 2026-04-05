#!/usr/bin/env python3
"""Export OpenAPI spec from APIFlask app."""
import os, json

os.environ.setdefault('FLASK_CONFIG', 'test')
from easyun import create_app

app = create_app()
with app.app_context():
    spec = app.spec
    with open('openapi.json', 'w') as f:
        json.dump(spec, f, indent=2)
    print(f'Exported openapi.json: {len(spec["paths"])} paths, {len(spec["components"]["schemas"])} schemas')
