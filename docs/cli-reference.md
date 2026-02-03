# CLI Reference

Complete reference for all dual-apps commands.

## Global Options

```bash
dual_apps --version    # Show version
dual_apps --help       # Show help
```

## Commands

### `dual_apps init app`

Generate a standalone Django app.

```bash
dual_apps init app <name> [options]
```

**Arguments:**
- `name`: App name (snake_case)

**Options:**
| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--model` | `-m` | `{Name}` | Main model name |
| `--fields` | `-f` | None | Model fields (CSV) |
| `--api-only` | | False | Generate API only |
| `--frontend-only` | | False | Generate frontend only |
| `--docker/--no-docker` | | True | Include Docker files |
| `--i18n` | | False | Include i18n support |
| `--celery` | | False | Include Celery support |
| `--auth/--no-auth` | | True | Require authentication |
| `--interactive` | `-i` | False | Interactive wizard |
| `--config` | `-c` | None | Config file path |
| `--output` | `-o` | `.` | Output directory |

**Examples:**
```bash
# Basic app
dual_apps init app jobs

# With custom model
dual_apps init app jobs --model=JobPosting

# With fields
dual_apps init app products --fields="name:str,price:decimal,active:bool"

# API only
dual_apps init app api_service --api-only

# Interactive mode
dual_apps init app --interactive
```

### `dual_apps init project`

Generate a complete Django project.

```bash
dual_apps init project <name> [options]
```

**Arguments:**
- `name`: Project name

**Options:**
| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--apps` | `-a` | `jobs` | Apps to generate (CSV) |
| `--template` | `-t` | `default` | Project template |
| `--db` | | `postgres` | Database type |
| `--auth` | | `jwt` | Authentication type |
| `--docker/--no-docker` | | True | Include Docker files |
| `--i18n` | | False | Include i18n support |
| `--celery` | | False | Include Celery support |
| `--interactive` | `-i` | False | Interactive wizard |
| `--config` | `-c` | None | Config file path |
| `--output` | `-o` | `.` | Output directory |

**Examples:**
```bash
# Basic project
dual_apps init project myproject

# Multiple apps
dual_apps init project myproject --apps=jobs,users,products

# With all options
dual_apps init project myproject \
    --apps=jobs,users \
    --db=postgres \
    --auth=jwt \
    --celery \
    --docker

# Interactive mode
dual_apps init project --interactive
```

### `dual_apps add app`

Add an app to an existing project.

```bash
dual_apps add app <name> [options]
```

**Options:**
| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--to` | `-t` | `.` | Project directory |
| `--model` | `-m` | None | Model name |
| `--fields` | `-f` | None | Model fields |

**Example:**
```bash
dual_apps add app products --to=myproject --model=Product
```

### `dual_apps config`

Generate a configuration file.

```bash
dual_apps config [options]
```

**Options:**
| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--output` | `-o` | `dual-apps.yaml` | Output file |
| `--format` | `-f` | `yaml` | Format (yaml/json) |

**Example:**
```bash
dual_apps config --output=myconfig.yaml
```

### `dual_apps info`

Show package information.

```bash
dual_apps info
```

## Field Types

When specifying fields with `--fields`:

| Type | Django Field | Example |
|------|--------------|---------|
| `str` | CharField | `name:str` |
| `text` | TextField | `description:text` |
| `int` | IntegerField | `count:int` |
| `decimal` | DecimalField | `price:decimal` |
| `bool` | BooleanField | `active:bool` |
| `date` | DateField | `birth_date:date` |
| `datetime` | DateTimeField | `created_at:datetime` |
| `uuid` | UUIDField | `external_id:uuid` |
| `email` | EmailField | `email:email` |
| `url` | URLField | `website:url` |

## Configuration File Format

```yaml
project:
  name: myproject
  apps:
    - jobs
    - users
  template: default
  db: postgres
  docker: true
  celery: false

apps:
  jobs:
    model: JobPosting
    fields:
      - name: title
        type: str
      - name: salary
        type: decimal

options:
  auth: jwt
```
