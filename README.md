# Easyun Server

[中文文档](docs/README_zh.md)

AWS cloud resource management platform — API server.

- Python 3.12+, built with APIFlask (lightweight Flask-based API framework)
- Auto-generated OpenAPI spec and Swagger UI at `/api/docs`
- Data validation via marshmallow schemas
- AWS resource management via Boto3 SDK
- Multi-cloud ready architecture with provider abstraction layer

## Tech Stack

| Component | Version |
|---|---|
| Python | ≥3.12 |
| Flask | 3.1 |
| APIFlask | 3.1 |
| Flask-SQLAlchemy | 3.1 |
| Flask-Migrate | 4.1 |
| marshmallow | 4.x |
| boto3 | 1.36+ |
| uv | Package manager |

## Quick Start

```bash
git clone https://github.com/aleck31/Easyun.git
cd Easyun/server

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env to set SECRET_KEY, database URI, etc.

# Initialize database
uv run flask initdb

# Run
uv run python run.py
```

API docs: http://127.0.0.1:6660/api/docs

## Project Structure

```
easyun-server/
├── easyun/                         # Main package
│   ├── common/                     # Shared components (auth, models, schemas)
│   ├── providers/                  # Cloud provider SDK (multi-cloud architecture)
│   │   ├── base.py                 # Abstract base classes
│   │   └── aws/                    # AWS implementation
│   │       ├── resource/           # Cloud resources by type
│   │       │   ├── compute/        # EC2, AMI, Instance Types
│   │       │   ├── storage/        # S3, EBS
│   │       │   ├── network/        # VPC, Subnet, SG, ELB, etc.
│   │       │   └── database/       # RDS
│   │       └── management/         # Pricing, Quotas, Cost, Tagging
│   ├── modules/                    # API blueprints
│   │   ├── dashboard/              # Monitoring dashboard
│   │   ├── datacenter/             # VPC / datacenter management
│   │   ├── mserver/                # EC2 server management
│   │   ├── mstorage/               # S3 + EBS storage management
│   │   ├── mdatabase/              # RDS database management
│   │   ├── mloadbalancer/          # ELB management
│   │   └── account/                # Account & keypair management
│   └── libs/                       # Utilities (task manager, logging)
├── config.py                       # Flask configuration
├── run.py                          # Entry point
└── pyproject.toml                  # Project config (uv)
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Commit your changes (`git commit -m 'feat: add some feature'`)
4. Push to the branch (`git push origin feat/my-feature`)
5. Open a Pull Request

Please follow [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `refactor:`, `docs:`, `build:`

## License

This project is licensed under the [Apache License 2.0](LICENSE).
