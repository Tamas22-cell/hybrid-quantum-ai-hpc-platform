# Security

This is a research prototype. Configure separate strong HPC_API_KEY and HPC_UI_PASSWORD secrets. Use HTTPS for remote access. The dashboard uses single-operator HTTP Basic authentication, not multi-tenant identity. Keep Redis, PostgreSQL and metrics private. Never expose raw worker or database ports. Report vulnerabilities privately via the repository's security reporting feature if enabled. No production security certification is claimed.
