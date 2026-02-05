#!/usr/bin/env python3
"""
OpenAPI to OpenClaw Skill Generator
====================================
Converts OpenAPI 3.x / Swagger 2.x specifications into ready-to-use OpenClaw skill folders.

Usage:
    python openapi_to_skill.py <spec_url_or_path> [--output <dir>] [--name <skill-name>]

Examples:
    python openapi_to_skill.py https://petstore3.swagger.io/api/v3/openapi.json
    python openapi_to_skill.py ./my-api.yaml --name my-api-skill --output ./skills/
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

# Try to import yaml, fall back gracefully
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Try to import httpx for URL fetching
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


def fetch_spec(source: str) -> Tuple[Dict[str, Any], str]:
    """Fetch OpenAPI spec from URL or file path. Returns (spec_dict, format)."""
    
    # Check if it's a URL
    if source.startswith(('http://', 'https://')):
        if not HAS_HTTPX:
            # Fallback to urllib
            import urllib.request
            with urllib.request.urlopen(source) as response:
                content = response.read().decode('utf-8')
        else:
            response = httpx.get(source, follow_redirects=True, timeout=30)
            response.raise_for_status()
            content = response.text
        
        # Detect format
        if source.endswith('.yaml') or source.endswith('.yml'):
            fmt = 'yaml'
        else:
            fmt = 'json'
    else:
        # It's a file path
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"Spec file not found: {source}")
        
        content = path.read_text()
        fmt = 'yaml' if path.suffix in ('.yaml', '.yml') else 'json'
    
    # Parse
    if fmt == 'yaml':
        if not HAS_YAML:
            raise ImportError("PyYAML required for YAML specs. Install with: pip install pyyaml")
        spec = yaml.safe_load(content)
    else:
        spec = json.loads(content)
    
    return spec, fmt


def detect_openapi_version(spec: Dict[str, Any]) -> str:
    """Detect if spec is OpenAPI 3.x or Swagger 2.x."""
    if 'openapi' in spec:
        return 'openapi3'
    elif 'swagger' in spec:
        return 'swagger2'
    else:
        raise ValueError("Unknown spec format: missing 'openapi' or 'swagger' field")


def normalize_name(name: str) -> str:
    """Convert a name to a valid identifier (snake_case)."""
    # Replace non-alphanumeric with underscore
    name = re.sub(r'[^a-zA-Z0-9]+', '_', name)
    # Remove leading/trailing underscores
    name = name.strip('_')
    # Convert to lowercase
    return name.lower()


def slugify(text: str) -> str:
    """Convert text to kebab-case slug."""
    text = re.sub(r'[^a-zA-Z0-9]+', '-', text.lower())
    return text.strip('-')


def extract_base_url(spec: Dict[str, Any], version: str) -> str:
    """Extract base URL from spec."""
    if version == 'openapi3':
        servers = spec.get('servers', [])
        if servers:
            return servers[0].get('url', '')
        return ''
    else:  # swagger2
        host = spec.get('host', '')
        basePath = spec.get('basePath', '')
        schemes = spec.get('schemes', ['https'])
        scheme = schemes[0] if schemes else 'https'
        if host:
            return f"{scheme}://{host}{basePath}"
        return basePath


def extract_security_schemes(spec: Dict[str, Any], version: str) -> Dict[str, Any]:
    """Extract security/authentication schemes."""
    if version == 'openapi3':
        components = spec.get('components', {})
        return components.get('securitySchemes', {})
    else:  # swagger2
        return spec.get('securityDefinitions', {})


def resolve_ref(spec: Dict[str, Any], ref: str) -> Dict[str, Any]:
    """Resolve a $ref pointer in the spec."""
    if not ref.startswith('#/'):
        return {}
    
    parts = ref[2:].split('/')
    current = spec
    for part in parts:
        # Handle URL encoding
        part = part.replace('~1', '/').replace('~0', '~')
        if isinstance(current, dict):
            current = current.get(part, {})
        else:
            return {}
    return current


def extract_schema_example(schema: Dict[str, Any], spec: Dict[str, Any], depth: int = 0) -> Any:
    """Generate an example value from a schema."""
    if depth > 5:
        return "..."
    
    # Handle $ref
    if '$ref' in schema:
        resolved = resolve_ref(spec, schema['$ref'])
        return extract_schema_example(resolved, spec, depth + 1)
    
    # Check for explicit example
    if 'example' in schema:
        return schema['example']
    if 'default' in schema:
        return schema['default']
    
    schema_type = schema.get('type', 'object')
    
    if schema_type == 'string':
        fmt = schema.get('format', '')
        if fmt == 'date':
            return "2026-02-04"
        elif fmt == 'date-time':
            return "2026-02-04T12:00:00Z"
        elif fmt == 'email':
            return "user@example.com"
        elif fmt == 'uuid':
            return "550e8400-e29b-41d4-a716-446655440000"
        elif 'enum' in schema:
            return schema['enum'][0]
        return "string"
    elif schema_type == 'integer':
        return 0
    elif schema_type == 'number':
        return 0.0
    elif schema_type == 'boolean':
        return True
    elif schema_type == 'array':
        items = schema.get('items', {})
        return [extract_schema_example(items, spec, depth + 1)]
    elif schema_type == 'object':
        props = schema.get('properties', {})
        result = {}
        for key, prop_schema in props.items():
            result[key] = extract_schema_example(prop_schema, spec, depth + 1)
        return result
    
    return None


def extract_operations(spec: Dict[str, Any], version: str) -> List[Dict[str, Any]]:
    """Extract all operations from the spec."""
    operations = []
    paths = spec.get('paths', {})
    
    for path, path_item in paths.items():
        # Path-level parameters
        path_params = path_item.get('parameters', [])
        
        for method in ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']:
            if method not in path_item:
                continue
            
            op = path_item[method]
            operation_id = op.get('operationId', f"{method}_{normalize_name(path)}")
            
            # Combine path and operation parameters
            all_params = path_params + op.get('parameters', [])
            
            # Extract request body (OpenAPI 3.x)
            request_body = None
            if version == 'openapi3' and 'requestBody' in op:
                rb = op['requestBody']
                content = rb.get('content', {})
                # Prefer JSON
                if 'application/json' in content:
                    schema = content['application/json'].get('schema', {})
                    request_body = {
                        'content_type': 'application/json',
                        'schema': schema,
                        'required': rb.get('required', False),
                        'example': extract_schema_example(schema, spec)
                    }
            
            # Extract responses
            responses = []
            for status, resp in op.get('responses', {}).items():
                resp_info = {
                    'status': status,
                    'description': resp.get('description', '')
                }
                # Try to get response schema
                if version == 'openapi3':
                    content = resp.get('content', {})
                    if 'application/json' in content:
                        resp_info['schema'] = content['application/json'].get('schema', {})
                else:  # swagger2
                    if 'schema' in resp:
                        resp_info['schema'] = resp['schema']
                responses.append(resp_info)
            
            operations.append({
                'operation_id': normalize_name(operation_id),
                'original_id': operation_id,
                'method': method.upper(),
                'path': path,
                'summary': op.get('summary', ''),
                'description': op.get('description', ''),
                'parameters': all_params,
                'request_body': request_body,
                'responses': responses,
                'tags': op.get('tags', []),
                'security': op.get('security', []),
                'deprecated': op.get('deprecated', False)
            })
    
    return operations


def generate_skill_md(
    spec: Dict[str, Any],
    version: str,
    operations: List[Dict[str, Any]],
    skill_name: str,
    base_url: str,
    security_schemes: Dict[str, Any]
) -> str:
    """Generate the SKILL.md content."""
    
    title = spec.get('info', {}).get('title', skill_name)
    description = spec.get('info', {}).get('description', f"Integration with {title} API")
    api_version = spec.get('info', {}).get('version', '1.0')
    
    # Build tool definitions for frontmatter
    # Group by tags
    tags_map: Dict[str, List[Dict[str, Any]]] = {}
    for op in operations:
        for tag in (op['tags'] or ['default']):
            tags_map.setdefault(tag, []).append(op)
    
    # Generate frontmatter description
    op_summaries = [op['summary'] or op['operation_id'] for op in operations[:10]]
    if len(operations) > 10:
        op_summaries.append(f"...and {len(operations) - 10} more")
    
    frontmatter_desc = (
        f"Auto-generated skill for {title} API (v{api_version}). "
        f"Provides {len(operations)} operations: {', '.join(op_summaries[:5])}. "
        f"Use when the user needs to interact with {title}."
    )
    
    # Truncate if too long
    if len(frontmatter_desc) > 500:
        frontmatter_desc = frontmatter_desc[:497] + "..."
    
    lines = [
        "---",
        f"name: {skill_name}",
        f"description: {frontmatter_desc}",
        "---",
        "",
        f"# {title}",
        "",
    ]
    
    if description:
        # Clean up description (first paragraph only for brevity)
        desc_clean = description.split('\n\n')[0].strip()
        lines.append(desc_clean)
        lines.append("")
    
    # Base URL and Auth section
    lines.append("## Configuration")
    lines.append("")
    lines.append(f"**Base URL:** `{base_url or '(set BASE_URL in environment)'}`")
    lines.append("")
    
    if security_schemes:
        lines.append("### Authentication")
        lines.append("")
        for name, scheme in security_schemes.items():
            scheme_type = scheme.get('type', 'unknown')
            if scheme_type == 'apiKey':
                location = scheme.get('in', 'header')
                key_name = scheme.get('name', 'X-API-Key')
                lines.append(f"- **{name}**: API Key in {location} (`{key_name}`)")
            elif scheme_type == 'http':
                http_scheme = scheme.get('scheme', 'bearer')
                lines.append(f"- **{name}**: HTTP {http_scheme.title()} authentication")
            elif scheme_type == 'oauth2':
                lines.append(f"- **{name}**: OAuth2 flow")
            elif scheme_type == 'openIdConnect':
                lines.append(f"- **{name}**: OpenID Connect")
            else:
                lines.append(f"- **{name}**: {scheme_type}")
        lines.append("")
    
    # Operations by tag
    lines.append("## Operations")
    lines.append("")
    
    for tag, tag_ops in tags_map.items():
        lines.append(f"### {tag.title()}")
        lines.append("")
        
        for op in tag_ops:
            deprecated = " ⚠️ DEPRECATED" if op['deprecated'] else ""
            lines.append(f"#### `{op['operation_id']}`{deprecated}")
            lines.append("")
            lines.append(f"**{op['method']}** `{op['path']}`")
            lines.append("")
            
            if op['summary']:
                lines.append(op['summary'])
                lines.append("")
            
            # Parameters
            if op['parameters']:
                lines.append("**Parameters:**")
                lines.append("")
                for param in op['parameters']:
                    # Resolve $ref if present
                    if '$ref' in param:
                        param = resolve_ref(spec, param['$ref'])
                    
                    name = param.get('name', 'unknown')
                    location = param.get('in', 'query')
                    required = "required" if param.get('required', False) else "optional"
                    param_type = param.get('schema', {}).get('type', param.get('type', 'string'))
                    desc = param.get('description', '')
                    
                    lines.append(f"- `{name}` ({location}, {param_type}, {required}): {desc}")
                lines.append("")
            
            # Request body
            if op['request_body']:
                rb = op['request_body']
                lines.append(f"**Request Body:** `{rb['content_type']}`")
                lines.append("")
                if rb['example']:
                    lines.append("```json")
                    lines.append(json.dumps(rb['example'], indent=2))
                    lines.append("```")
                    lines.append("")
            
            # Response
            success_responses = [r for r in op['responses'] if r['status'].startswith('2')]
            if success_responses:
                resp = success_responses[0]
                lines.append(f"**Response ({resp['status']}):** {resp['description']}")
                lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # Usage section
    lines.append("## Usage")
    lines.append("")
    lines.append("Use the `api_client.py` script to call any operation:")
    lines.append("")
    lines.append("```bash")
    lines.append(f"python scripts/api_client.py <operation_id> [--param value ...]")
    lines.append("```")
    lines.append("")
    lines.append("**Environment variables:**")
    lines.append("")
    lines.append(f"- `{skill_name.upper().replace('-', '_')}_BASE_URL`: API base URL")
    lines.append(f"- `{skill_name.upper().replace('-', '_')}_API_KEY`: API key (if required)")
    lines.append("")
    
    return '\n'.join(lines)


def generate_api_client(
    spec: Dict[str, Any],
    version: str,
    operations: List[Dict[str, Any]],
    skill_name: str,
    base_url: str,
    security_schemes: Dict[str, Any]
) -> str:
    """Generate the Python API client script."""
    
    env_prefix = skill_name.upper().replace('-', '_')
    
    code = f'''#!/usr/bin/env python3
"""
API Client for {spec.get('info', {}).get('title', skill_name)}
Auto-generated by OpenAPI to OpenClaw Skill Generator

Usage:
    python api_client.py <operation_id> [--param value ...]
    python api_client.py --list  # List all operations
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, Optional
from urllib.parse import urljoin, urlencode

# Configuration
BASE_URL = os.environ.get("{env_prefix}_BASE_URL", "{base_url}")
API_KEY = os.environ.get("{env_prefix}_API_KEY", "")
AUTH_HEADER = os.environ.get("{env_prefix}_AUTH_HEADER", "Authorization")

# Try httpx first, fall back to urllib
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    import urllib.request
    import urllib.error


def make_request(
    method: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    body: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Make an HTTP request to the API."""
    
    url = urljoin(BASE_URL.rstrip('/') + '/', path.lstrip('/'))
    
    # Build headers
    req_headers = {{"Content-Type": "application/json", "Accept": "application/json"}}
    if API_KEY:
        req_headers[AUTH_HEADER] = f"Bearer {{API_KEY}}"
    if headers:
        req_headers.update(headers)
    
    # Add query params
    if params and method.upper() == "GET":
        url = f"{{url}}?{{urlencode(params)}}"
    
    if HAS_HTTPX:
        with httpx.Client(timeout=30) as client:
            response = client.request(
                method=method,
                url=url,
                headers=req_headers,
                json=body if body else None,
                params=params if method.upper() != "GET" else None
            )
            response.raise_for_status()
            try:
                return response.json()
            except:
                return {{"status": response.status_code, "text": response.text}}
    else:
        # Fallback to urllib
        data = json.dumps(body).encode('utf-8') if body else None
        req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                content = resp.read().decode('utf-8')
                try:
                    return json.loads(content)
                except:
                    return {{"status": resp.status, "text": content}}
        except urllib.error.HTTPError as e:
            return {{"error": str(e), "status": e.code, "body": e.read().decode('utf-8')}}


# Operation definitions
OPERATIONS = {{
'''
    
    # Add each operation
    for op in operations:
        path_params = [p for p in op['parameters'] if p.get('in') == 'path']
        query_params = [p for p in op['parameters'] if p.get('in') == 'query']
        header_params = [p for p in op['parameters'] if p.get('in') == 'header']
        
        code += f'''    "{op['operation_id']}": {{
        "method": "{op['method']}",
        "path": "{op['path']}",
        "summary": """{op['summary']}""",
        "path_params": {json.dumps([p.get('name', '') for p in path_params])},
        "query_params": {json.dumps([p.get('name', '') for p in query_params])},
        "header_params": {json.dumps([p.get('name', '') for p in header_params])},
        "has_body": {op['request_body'] is not None},
    }},
'''
    
    code += '''}


def execute_operation(op_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an operation by ID with the given arguments."""
    
    if op_id not in OPERATIONS:
        raise ValueError(f"Unknown operation: {op_id}. Use --list to see available operations.")
    
    op = OPERATIONS[op_id]
    path = op["path"]
    
    # Substitute path parameters
    for param in op["path_params"]:
        if param in args:
            path = path.replace(f"{{{param}}}", str(args[param]))
    
    # Build query params
    query_params = {}
    for param in op["query_params"]:
        if param in args:
            query_params[param] = args[param]
    
    # Build headers
    headers = {}
    for param in op["header_params"]:
        if param in args:
            headers[param] = args[param]
    
    # Build body
    body = None
    if op["has_body"] and "body" in args:
        if isinstance(args["body"], str):
            body = json.loads(args["body"])
        else:
            body = args["body"]
    
    return make_request(
        method=op["method"],
        path=path,
        params=query_params if query_params else None,
        body=body,
        headers=headers if headers else None
    )


def list_operations():
    """Print all available operations."""
    print("Available operations:\\n")
    for op_id, op in OPERATIONS.items():
        print(f"  {op_id}")
        print(f"    {op['method']} {op['path']}")
        if op['summary']:
            print(f"    {op['summary']}")
        print()


def main():
    parser = argparse.ArgumentParser(description="API Client")
    parser.add_argument("operation", nargs="?", help="Operation ID to execute")
    parser.add_argument("--list", action="store_true", help="List all operations")
    parser.add_argument("--body", help="JSON body for POST/PUT/PATCH requests")
    
    # Add a catch-all for dynamic parameters
    args, unknown = parser.parse_known_args()
    
    if args.list:
        list_operations()
        return
    
    if not args.operation:
        parser.print_help()
        return
    
    # Parse unknown args as --key value pairs
    params = {}
    if args.body:
        params["body"] = args.body
    
    i = 0
    while i < len(unknown):
        if unknown[i].startswith("--"):
            key = unknown[i][2:]
            if i + 1 < len(unknown) and not unknown[i + 1].startswith("--"):
                params[key] = unknown[i + 1]
                i += 2
            else:
                params[key] = True
                i += 1
        else:
            i += 1
    
    try:
        result = execute_operation(args.operation, params)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
    
    return code


def generate_skill(
    source: str,
    output_dir: str,
    skill_name: Optional[str] = None
) -> str:
    """Main function to generate a skill from an OpenAPI spec."""
    
    print(f"📥 Fetching spec from: {source}")
    spec, fmt = fetch_spec(source)
    
    version = detect_openapi_version(spec)
    print(f"📋 Detected format: {version} ({fmt})")
    
    # Extract info
    title = spec.get('info', {}).get('title', 'api')
    if not skill_name:
        skill_name = slugify(title)
    
    print(f"🏷️  Skill name: {skill_name}")
    
    base_url = extract_base_url(spec, version)
    print(f"🌐 Base URL: {base_url or '(not specified)'}")
    
    security_schemes = extract_security_schemes(spec, version)
    print(f"🔐 Security schemes: {list(security_schemes.keys()) or ['none']}")
    
    operations = extract_operations(spec, version)
    print(f"⚙️  Found {len(operations)} operations")
    
    # Create skill directory
    skill_dir = Path(output_dir) / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / 'scripts').mkdir(exist_ok=True)
    (skill_dir / 'references').mkdir(exist_ok=True)
    
    # Generate SKILL.md
    skill_md = generate_skill_md(spec, version, operations, skill_name, base_url, security_schemes)
    (skill_dir / 'SKILL.md').write_text(skill_md)
    print(f"✅ Created: {skill_dir / 'SKILL.md'}")
    
    # Generate api_client.py
    api_client = generate_api_client(spec, version, operations, skill_name, base_url, security_schemes)
    (skill_dir / 'scripts' / 'api_client.py').write_text(api_client)
    os.chmod(skill_dir / 'scripts' / 'api_client.py', 0o755)
    print(f"✅ Created: {skill_dir / 'scripts' / 'api_client.py'}")
    
    # Save original spec for reference
    spec_filename = f"openapi.{fmt if fmt == 'yaml' else 'json'}"
    if fmt == 'yaml' and HAS_YAML:
        (skill_dir / 'references' / spec_filename).write_text(yaml.dump(spec, default_flow_style=False))
    else:
        (skill_dir / 'references' / spec_filename).write_text(json.dumps(spec, indent=2))
    print(f"✅ Created: {skill_dir / 'references' / spec_filename}")
    
    print(f"\n🎉 Skill generated successfully at: {skill_dir}")
    return str(skill_dir)


def main():
    parser = argparse.ArgumentParser(
        description="Generate OpenClaw skill from OpenAPI/Swagger specification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://petstore3.swagger.io/api/v3/openapi.json
  %(prog)s ./my-api.yaml --name my-api-skill
  %(prog)s https://api.example.com/v1/openapi.json --output ./skills/
        """
    )
    parser.add_argument("spec", help="URL or path to OpenAPI/Swagger spec (JSON or YAML)")
    parser.add_argument("--output", "-o", default=".", help="Output directory (default: current)")
    parser.add_argument("--name", "-n", help="Skill name (default: derived from spec title)")
    
    args = parser.parse_args()
    
    try:
        generate_skill(args.spec, args.output, args.name)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
