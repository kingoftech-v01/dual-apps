# CLI Reference

Complete reference for all dual-apps CLI commands.

![Generation Workflow](images/generation-workflow.svg)

## Global Options

```bash
dual_apps --version    # Show version
dual_apps --help       # Show help
```

## Commands

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
| `--apps` | `-a` | `core` | Apps to generate (CSV) |
| `--template` | `-t` | `default` | Template: default, ecommerce, blog, saas, cms, booking, marketplace |
| `--type` | | `fullstack` | Project type: backend, frontend, fullstack |
| `--db` | | `postgres` | Database: postgres, mysql, sqlite |
| `--auth` | | `jwt` | Authentication: jwt, session, allauth |
| `--jwt-storage` | | `httpOnly` | JWT storage: httpOnly, localStorage |
| `--frontend` | `-f` | `htmx` | Frontend: html, htmx, react |
| `--css` | `-c` | `bootstrap` | CSS framework: bootstrap, tailwind |
| `--docker/--no-docker` | | True | Include Docker files |
| `--i18n` | | False | Include i18n support |
| `--celery` | | False | Include Celery support |
| `--interactive` | `-i` | False | Interactive wizard |
| `--config` | | None | Config file path |
| `--output` | `-o` | `.` | Output directory |

**Examples:**
```bash
# Basic project
dual_apps init project myproject

# Multiple apps
dual_apps init project myproject --apps=jobs,users,products

# Ecommerce store with React
dual_apps init project myshop \
    --template=ecommerce \
    --frontend=react \
    --css=tailwind

# SaaS with HTMX and Celery
dual_apps init project mysaas \
    --template=saas \
    --frontend=htmx \
    --css=bootstrap \
    --celery

# Blog with basic HTML
dual_apps init project myblog \
    --template=blog \
    --frontend=html

# CMS with internationalization
dual_apps init project mycms \
    --template=cms \
    --i18n

# Booking system
dual_apps init project mybooking \
    --template=booking \
    --frontend=react

# Marketplace
dual_apps init project mymarket \
    --template=marketplace \
    --frontend=react

# Backend-only API
dual_apps init project myapi \
    --type=backend \
    --auth=jwt

# With all options
dual_apps init project myproject \
    --apps=jobs,users \
    --template=saas \
    --type=fullstack \
    --db=postgres \
    --auth=jwt \
    --jwt-storage=httpOnly \
    --frontend=htmx \
    --css=tailwind \
    --docker \
    --celery \
    --i18n

# Interactive mode
dual_apps init project --interactive
```

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

# Full featured
dual_apps init app users \
    --model=UserProfile \
    --auth \
    --i18n \
    --docker \
    --celery

# Interactive mode
dual_apps init app --interactive
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

### `dual_apps help`

Show help for a topic.

```bash
dual_apps help [topic]
```

**Topics:**
| Topic | Description |
|-------|-------------|
| `overview` | General overview |
| `commands` | Available commands |
| `templates` | Template types |
| `quickstart` | Quick start guide |
| `config` | Configuration file |
| `examples` | Example commands |

**Examples:**
```bash
dual_apps help
dual_apps help templates
dual_apps help quickstart
```

### `dual_apps info`

Show package information.

```bash
dual_apps info
```

## Template Types

| Template | Description | Default Apps |
|----------|-------------|--------------|
| `default` | Standard project | core |
| `ecommerce` | Online store | shop, cart, orders |
| `blog` | Content platform | blog, comments |
| `saas` | SaaS application | subscriptions, billing |
| `cms` | Content management | pages, media |
| `booking` | Reservation system | services, appointments |
| `marketplace` | Multi-vendor platform | listings, sellers |

## Frontend Options

| Frontend | Description | Features |
|----------|-------------|----------|
| `html` | Basic HTML templates | Server-rendered, no JS |
| `htmx` | HTMX + Alpine.js | Dynamic updates, auth flow |
| `react` | React SPA with Vite | JWT auth, API client |

## CSS Frameworks

| Framework | Description |
|-----------|-------------|
| `bootstrap` | Bootstrap 5 with responsive grid |
| `tailwind` | Utility-first CSS framework |

## JWT Storage Options

| Option | Description | Security |
|--------|-------------|----------|
| `httpOnly` | Stored in httpOnly cookies | More secure (default) |
| `localStorage` | Stored in browser localStorage | Less secure |

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
# dual-apps.yaml
project:
  name: myproject
  template: ecommerce
  type: fullstack
  apps:
    - shop
    - cart
    - orders

database:
  engine: postgres
  name: myproject_db

auth:
  type: jwt
  jwt_storage: httpOnly

frontend:
  framework: react
  css: tailwind

features:
  docker: true
  celery: true
  i18n: false

apps:
  shop:
    model: Product
    fields:
      - name: title
        type: str
      - name: price
        type: decimal
      - name: stock
        type: int
```

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | File/directory exists |
| 4 | Template not found |
