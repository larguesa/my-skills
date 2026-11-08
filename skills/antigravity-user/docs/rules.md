# Rules

Available on: Antigravity App, Antigravity CLI, Antigravity IDE

Rules are persistent instructions, coding standards, and architectural constraints that shape how Antigravity behaves in your codebase. Unlike chat prompts that apply to a single conversation, Antigravity automatically discovers rules from your filesystem and injects them into the agent’s context.

Tip

**Rule vs. Skill**: Write a **rule** for _constraints and invariants_ (for example, “Always use `zod` for validation” or “Never import `internal/` across packages”). Write a **[skill](/docs/skills)** for _multi-step workflows_ (for example, “How to run database migrations”).

## Where rules are stored

Antigravity discovers rules in two scopes: your workspace, including parent folders up to the repository root, and your global configuration. Rules are **cumulative** rather than replacement-based: Antigravity combines all the rules it finds into the prompt.

### Directory-scoped rules

You can place an `AGENTS.md` or `GEMINI.md` file—or a `.agents/rules/` directory—in your workspace folder and in any parent folder up to the repository root. Antigravity loads rules at each of these levels:

*   `<dir>/AGENTS.md` or `<dir>/GEMINI.md`
*   `<dir>/.agents/AGENTS.md` or `<dir>/.agents/GEMINI.md`
*   `<dir>/.agents/rules/*.md` _(and legacy `<dir>/.agent/rules/*.md`)_

Antigravity doesn’t load rules from subfolders below the workspace folder, even when the agent reads or edits files there. For details, see [Customization discovery](/docs/customization-discovery#workspace-folders-and-parent-directories).

### Global rules

Global rules apply across **all** projects on your workstation:

*   **Standalone global files** (no frontmatter needed, always active): `~/.gemini/AGENTS.md`, `~/.gemini/GEMINI.md`, `~/.gemini/config/AGENTS.md`, or `~/.gemini/config/GEMINI.md`
*   **Modular global rules** (YAML frontmatter required): `~/.gemini/config/rules/*.md`

Caution

**Flat directory scanning**: Antigravity scans only immediate `.md` children inside `.agents/rules/` (such as `.agents/rules/typescript.md`). Antigravity ignores files nested in subdirectories (such as `.agents/rules/frontend/react.md`) unless you explicitly register them in `.agents/rules.json`.

## YAML frontmatter and activation modes

Frontmatter requirements depend on the file type:

1.  **`AGENTS.md` and `GEMINI.md` do not use frontmatter.** Antigravity treats its entire content as plain Markdown and keeps it continuously active (`always_on`).
2.  **Every `.md` file inside `rules/` must start with YAML frontmatter** declaring a valid `trigger`.

Caution

**Missing frontmatter or invalid `trigger`**: If a file in `.agents/rules/*.md` omits frontmatter or specifies an unrecognized `trigger` value (such as camelCase `alwaysOn` or `modelDecision`), Antigravity silently discards the rule.

### Supported frontmatter keys

Rules in `.agents/rules/` support the following YAML frontmatter keys:

```yaml
---
trigger: model_decision       # Required: always_on | model_decision | glob | manual
description: "..."            # Required for model_decision; recommended for all rules
globs: "*.ts, *.tsx"          # Required for glob (singular `glob:` is also accepted)
---
```

| Field | Type | Required | Description |
| :-- | :-- | :-- | :-- |
| `trigger` | `string` | **Yes** | Controls how and when the rule activates: `model_decision`, `always_on`, `glob`, or `manual`. |
| `description` | `string` | **Required** for `model_decision` | Concise summary of when the rule applies. Antigravity injects this summary into the prompt index for `model_decision` rules, and uses it as fallback context if an `always_on` rule exceeds the token budget. |
| `globs` _(or `glob`)_ | `string` | **Required** for `glob` | Comma-separated file glob patterns (for example, `"*.py, *_test.py"`). Wrap patterns starting with `*` in quotes so YAML does not treat `*` as an alias anchor. |

### Activation modes

Configure the `trigger` key to control how and when a rule is loaded into context:

*   **`model_decision`** _(best for detailed domain guides)_: Antigravity injects only the rule’s path and `description` upfront (progressive disclosure). The agent reads the full rule on demand when your task matches the description.
    
    ```markdown
    ---
    trigger: model_decision
    description: "Apply these guidelines whenever writing or reviewing database migrations or SQL schema changes."
    ---
    
    # Database Migration Rules
    
    1. Never drop or rename a column in a single deployment; use an expand-and-contract migration.
    2. Always add `CONCURRENTLY` when creating indexes on existing tables in PostgreSQL.
    ```
    
*   **`always_on`** _(always active in scope)_: Antigravity injects the full content into the system prompt on every turn. Prefer placing `always_on` rules directly in `AGENTS.md` when you do not need frontmatter.
    
*   **`glob`** _(file-pattern scoped)_: Automatically activates when the agent interacts with files matching any comma-separated pattern in `globs`:
    
    ```markdown
    ---
    trigger: glob
    globs: "*.proto, **/*.pb.go"
    description: "Protobuf schema design and backward-compatibility rules."
    ---
    
    # Protobuf Conventions
    
    * Never reuse a deleted field number; always mark both the field number and name as `reserved`.
    ```
    
*   **`manual`** _(explicit `@` mention only)_: Antigravity never loads these rules automatically. Antigravity adds the rule to your message only when you [`@`\-mention it](/docs/at-mentions) (ideal for release checklists or audit rubrics). The Antigravity CLI doesn’t support rule mentions.
    

## Advanced features and limits

### File includes

Inside any rule file (`AGENTS.md`, `GEMINI.md`, or `.agents/rules/*.md`), Antigravity supports two distinct `@` syntaxes for referencing files:

*   **`@[label](path)`**: Inlines the target file’s contents directly into the rule before prompt evaluation and size-limit checks.
    *   **Path resolution**: Antigravity resolves relative paths from the directory containing the rule file. Paths starting with `~/` expand to your user home directory.
    *   **Frontmatter stripping**: If an included file contains YAML frontmatter, Antigravity strips the frontmatter and splices in only the Markdown body.
*   **`@filename`**: Does **not** inline file contents. Instead, it resolves the path (relative to the rule file, or as a workspace-relative/absolute path) and rewrites it to a canonical absolute workspace path (`@/workspace/path`) so the agent has an unambiguous file reference.

```markdown
Follow our shared API design standards:
@[API Design Standards](../docs/api-standards.md)

When updating database models, check @src/db/schema.ts first.
```

### Sharing rules across projects

To share rules stored outside `.agents/rules/` or to include nested subdirectories of rules while preserving their YAML frontmatter and triggers, create `.agents/rules.json`:

```json
{
  "inherits": [
    { "path": "../shared-config/.agents/rules.json" }
  ],
  "entries": [
    {
      "path": "../shared-rules",
      "exclude": ["deprecated_rules.md", "draft_rules.md"]
    },
    {
      "path": ".agents/rules",
      "include_only": ["frontend/react.md"]
    }
  ]
}
```

### Size limits and token budgets

To prevent rules from exhausting the context window, Antigravity enforces two limits:

1.  **24 KB (`24,000` bytes) per-file limit**: Antigravity truncates any single rule file that exceeds 24,000 bytes (after expanding `@[label](path)` includes).
2.  **20,000-token aggregate rules budget**: All active global and `always_on` rules share a 20,000-token budget separate from the customization budget (plugins such as skills and MCP). If the total exceeds 20,000 tokens, Antigravity automatically demotes the largest rule files from inline text to lightweight pointers (`- <path>: <description>`), allowing the agent to read them on demand.

## Configuration by surface

Select your surface below to configure global or workspace-specific rules:

### Antigravity App

#### Managing rules in the Antigravity App

Follow these steps to create or manage rules in the Antigravity App:

1.  Open the **Customizations** panel from the application menu or project settings.
2.  Select the **Rules** tab.
3.  Click **\+ Global** to create global rules, or **\+ Workspace** to create rules scoped to the active project.

#### Antigravity App file locations

The Antigravity App loads rules from the following locations:

*   **Workspace rules**: `AGENTS.md`, `GEMINI.md`, or `.agents/rules/*.md` in a project folder or any parent folder up to the repository root.
*   **Global rules**: `~/.gemini/AGENTS.md`, `~/.gemini/GEMINI.md`, `~/.gemini/config/AGENTS.md`, `~/.gemini/config/GEMINI.md`, or modular rules in `~/.gemini/config/rules/*.md`.

### Antigravity CLI

#### Managing rules in Antigravity CLI

The Antigravity CLI evaluates workspace, directory-scoped, global, and plugin rules during prompt expansion:

*   **Workspace and directory rules**: `AGENTS.md`, `GEMINI.md`, or `.agents/rules/*.md` in the folder where you start `agy` or any parent folder up to the repository root.
*   **Global rules**: `~/.gemini/AGENTS.md`, `~/.gemini/GEMINI.md`, `~/.gemini/config/AGENTS.md`, `~/.gemini/config/GEMINI.md`, or `~/.gemini/config/rules/*.md`.
*   **Plugin rules**: Antigravity automatically activates rules packaged inside installed [plugins](/docs/plugins) under `~/.gemini/config/plugins/<plugin-folder>/rules/`.

### Antigravity IDE & Extensions

#### Managing rules in Antigravity IDE and extensions

Follow these steps to create or manage rules in Antigravity IDE and extensions:

1.  Click the **…** menu at the top of the agent side panel.
2.  Select **Customizations**, then navigate to the **Rules** tab.
3.  Click **\+ Global** to author workstation-wide rules, or **\+ Workspace** to create project-specific rules.

#### Antigravity IDE and extensions file locations

Antigravity IDE and extensions load rules from the following locations:

*   **Workspace rules**: `AGENTS.md`, `GEMINI.md`, or `.agents/rules/*.md` in your project folder or any parent folder up to the repository root.
*   **Global rules**: `~/.gemini/AGENTS.md`, `~/.gemini/GEMINI.md`, or `~/.gemini/config/rules/*.md`.