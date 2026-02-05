---
name: openapi-integrator
description: Generate OpenClaw skills from OpenAPI/Swagger specifications. Use when you need to integrate with a REST API that has an OpenAPI spec, create a skill from a swagger.json/openapi.yaml file, or auto-generate API client code. Supports OpenAPI 3.x and Swagger 2.x.
---

# OpenAPI Integrator

Transform any OpenAPI/Swagger specification into a ready-to-use OpenClaw skill with a single command.

## Quick Start

```bash
# From URL
python skills/openapi-integrator/scripts/openapi_to_skill.py https://petstore3.swagger.io/api/v3/openapi.json --output skills/

# From local file
python skills/openapi-integrator/scripts/openapi_to_skill.py ./my-api.yaml --name my-api --output skills/
```

## What It Generates

For each API spec, the generator creates:

```
skill-name/
├── SKILL.md              # Full skill documentation with all operations
├── scripts/
│   └── api_client.py     # Ready-to-use Python client
└── references/
    └── openapi.json      # Original spec for reference
```

## Features

- **Auto-detection**: Handles OpenAPI 3.x and Swagger 2.x
- **Format support**: JSON and YAML specs (local or remote)
- **Security mapping**: Extracts API key, Bearer, OAuth2 schemes
- **Operation grouping**: Organizes by tags for clean documentation
- **Example generation**: Creates request body examples from schemas
- **Zero dependencies**: Works with just Python stdlib (httpx/pyyaml optional)

## Generated Client Usage

The generated `api_client.py` provides:

```bash
# List all operations
python scripts/api_client.py --list

# Call an operation
python scripts/api_client.py get_pet_by_id --petId 123

# POST with body
python scripts/api_client.py create_pet --body '{"name": "Fluffy", "status": "available"}'
```

## Environment Variables

Set these in your environment or `.env`:

- `{SKILL_NAME}_BASE_URL`: Override the API base URL
- `{SKILL_NAME}_API_KEY`: API key for authentication
- `{SKILL_NAME}_AUTH_HEADER`: Custom auth header name (default: `Authorization`)

## Common APIs to Try

| API | Spec URL |
|-----|----------|
| Petstore | `https://petstore3.swagger.io/api/v3/openapi.json` |
| GitHub | `https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.json` |
| Stripe | `https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json` |

## Troubleshooting

**YAML parsing fails?**
```bash
pip install pyyaml
```

**HTTPS fetch fails?**
```bash
pip install httpx
```

**Large specs timeout?**
Download locally first, then run on the local file.
