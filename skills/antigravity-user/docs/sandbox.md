# Terminal sandbox

Available on: Antigravity App, Antigravity CLI

The terminal sandbox isolates agent shell commands inside OS-level container boundaries to protect your workstation and sensitive files.

## Antigravity App

### Updated permission settings

#### Overview

Antigravity includes a **terminal sandbox**, enabled by default, that isolates shell commands executed by agents. Sandboxed commands can write to your project folders, temporary directories, and common build caches, and read system directories such as `/usr` and `/etc` so your tools keep working. Sensitive files such as `~/.ssh` and `.env` are blocked, anything not explicitly mounted is invisible inside the sandbox, and network access is limited to domains you’ve approved.

The sandbox is built on native operating system primitives, so there are no virtual machines or Docker images to manage and no startup delay:

| Operating System | Technology | Details |
| :-- | :-- | :-- |
| **Linux** | Namespaces | Kernel namespaces isolate the filesystem, hide host processes, and cut off networking. |
| **macOS** | `sandbox-exec` | Seatbelt profiles (SBPL) restrict filesystem access and socket connections. |

#### Configuration

Your **permission preset** controls whether the sandbox is used:

| Preset | Sandbox | Commands |
| :-- | :-- | :-- |
| **Request Review** | Off | Always ask |
| **Default** _(default)_ | On | Allowed in sandbox; ask outside |
| **Auto** | On | Allowed in sandbox; safe, reversible commands allowed outside |
| **Turbo** | Off | Allowed without prompting, unrestricted |

You can change your preset in three places:

*   **For all projects**: Open **Settings** > **General** > **Global Permissions** > **Permission Preset** (**Permissions** > **This Computer** if remote agents are available to you).
*   **For a single project**: Override the global preset under **Settings** > **Projects**. Projects default to **Inherit Global** upon creation, which follows your global preset.
*   **From the message box** (`v2.23.0+`): Choose a preset from the permissions picker. The picker changes your global preset, or the project’s preset if the project overrides it. To remove a project override, choose **Use Global Settings**.

Refer to **[Agent permissions](/docs/permissions)** for the full preset behavior, including file access, MCP tools, and web page reads.

Note

**Default** is selected by default (**Request Review** if the sandbox isn’t available). **Auto** (shown as **Auto (Preview)** in version 2.29.0 and earlier) is available in `v2.23.0+` on macOS and Linux and `v2.26.0+` on Windows when the sandbox is available. It isn’t currently available for business or enterprise accounts, including [Antigravity in Gemini Enterprise](/docs/enterprise).

#### Unsandboxed commands

Some commands cannot work inside the sandbox—for example, those needing network access or talking to system services. The agent can request to run such commands outside the sandbox, where they run on your host with full privileges:

*   **Default**: Requests to run outside the sandbox always pause for your approval, unless the command is already covered by a `command` allow or deny rule.
*   **Auto** (`v2.23.0+` on macOS and Linux, `v2.26.0+` on Windows): Antigravity automatically checks commands that need to run outside the sandbox so safe, reversible commands run without prompting, while risky or irreversible commands still pause for your approval (unless covered by a `command` allow or deny rule).

To let a specific command run without prompting—inside or outside the sandbox—add a `command` allow rule:

```text
command(git push)
command(regex:docker compose .*)
```

#### Permissions integration

The sandbox derives its access boundaries from your **[Permissions](/docs/permissions)** configuration:

*   **Filesystem**: Your project folders are mounted read-write. Paths allowed under `read_file` are mounted read-only, and paths allowed under `write_file` are mounted read-write, on top of the default system mounts. Everything else is inaccessible.
*   **Network**: Sandboxed commands run without network access by default. Domains allowed under `read_url` are added to the sandbox’s outbound allowlist.

### Previous permission settings

Note

Business and enterprise accounts use the behavior described in this section.

#### Overview

Antigravity includes a **terminal sandbox** that isolates shell commands executed by agents. Sandboxed commands can write to your project folders, temporary directories, and common build caches, and read system directories so your tools keep working. Sensitive files such as `.env` are blocked, and network access is limited to domains you’ve approved. On macOS and Linux, anything not explicitly mounted is invisible inside the sandbox. On Windows, the sandbox requires Windows 11 24H2 or later with the August 2026 update or later, and folders outside your user profile are readable but not writable inside it.

#### Configuration

You can configure the sandbox globally or per project.

##### Global settings

In **Settings** > **General**, under **Agent Settings**, configure the following options:

*   **Enable Sandbox Mode (Preview)**: Runs agent terminal commands inside the sandbox.
*   **Terminal Command Auto Execution**: Set to **Proceed in Sandbox** to let sandboxed commands run without approval; commands that need to run outside the sandbox still ask first. The other options are **Require Review** and **Always Proceed**.

##### Project settings

Select a project under **Settings** > **Projects** to override these settings for that project. Each setting gains an **Inherit Global** option, and **Enable Sandbox Mode** becomes a dropdown: **Inherit Global**, **Enabled**, or **Disabled**.

#### Security presets

The **Security Preset** dropdown in the same settings section bundles the terminal and file access policies:

| Preset | Terminal Command Auto Execution | Outside-of-folders file access |
| :-- | :-- | :-- |
| **Default** | Require Review | Always Ask |
| **Full machine** | Require Review | Allow |
| **Turbo mode** | Always Proceed | Allow |

None of the presets turn the sandbox on. Enabling **Enable Sandbox Mode** switches the preset to **Custom**, where you set each option yourself—a common combination is the sandbox with **Proceed in Sandbox**.

#### Unsandboxed commands

When a command needs to run outside the sandbox—because it matches an `unsandboxed(...)` rule, the agent requested it, or the sandbox is disabled—the command runs on your host with full privileges. Depending on your execution policy, the agent pauses for your approval first.

#### Permissions integration

The sandbox derives its access boundaries from your **[Permissions](/docs/permissions)** configuration:

*   **Filesystem**: Your project folders are mounted read-write. Paths allowed under `read_file` are mounted read-only, and paths allowed under `write_file` are mounted read-write, on top of the default system mounts. Everything else is inaccessible, except that on Windows, folders outside your user profile stay readable.
*   **Network**: When network access is enabled, domains allowed under `read_url` are added to the sandbox’s outbound allowlist.
*   **Escape hatches (`unsandboxed`)**: To let specific commands run outside the sandbox without disabling it entirely, add an `unsandboxed` allow rule:
    
    ```text
    unsandboxed(git push)
    unsandboxed(docker compose .*)
    ```

## Antigravity CLI

### How it works

With the terminal sandbox enabled, Antigravity CLI executes commands inside an OS-level isolation boundary. Commands can write to your workspace, temporary directories, and common build caches, and read system directories (such as `/usr` and `/etc` on macOS and Linux) so your tools keep working. Sensitive files such as `~/.ssh` and `.env` are blocked, and network access is limited to domains you’ve approved. On macOS and Linux, anything not explicitly mounted is invisible inside the sandbox. On Windows, folders outside your user profile are readable but not writable inside the sandbox, and other files in your user profile and other users’ profiles stay hidden.

The sandbox is built on native operating system primitives, so there are no virtual machines or Docker images to manage and no startup delay:

| Operating System | Technology | Details |
| :-- | :-- | :-- |
| **Linux** | Namespaces | Kernel namespaces isolate the filesystem, hide host processes, and cut off networking. |
| **macOS** | `sandbox-exec` | Seatbelt profiles (SBPL) restrict filesystem access and socket connections. |
| **Windows** | Process security environments | Commands run in an AppContainer inside a process security environment, which restricts filesystem and network access. Requires Windows 11 24H2 or later with the August 2026 update or later. |

### CLI configuration

`auto` mode enables the terminal sandbox automatically. In other modes, including `default` mode, enable the sandbox in `~/.gemini/antigravity-cli/settings.json` or interactively using `/config`:

```json
{
    "enableTerminalSandbox": true,
    "toolPermission": "proceed-in-sandbox"
}
```

The configuration supports the following settings:

*   **`agentMode`** (string, default: `""`, which is `default` mode): Setting `"agentMode": "auto"` enables the terminal sandbox automatically so commands run inside the sandbox by default, and automatically evaluates commands that need to run outside the sandbox so safe, reversible commands run without prompting while risky or irreversible commands pause for approval. Refer to [Choose an execution mode](/docs/cli/modes).
*   **`enableTerminalSandbox`** (boolean, default: `false`): Runs agent commands inside the sandbox. `auto` mode turns it on automatically.
*   **`toolPermission`** (string, default: `"request-review"`): Outside `auto` mode, setting this to `"proceed-in-sandbox"` lets sandboxed commands run automatically, while commands that need to run outside the sandbox still prompt for review. Refer to [Settings](/docs/settings) for the other modes.

Note

`auto` mode is available in `v1.3.5+` on **macOS and Linux** and `v1.4.4+` on **Windows** for personal accounts when the sandbox is available.

#### CLI flags

You can also control sandboxing when launching the CLI:

```bash
# Force the sandbox on for this session
agy --sandbox

# Launch in auto mode (enables the sandbox and automatically evaluates commands that need to run outside it)
agy --mode=auto
```

The CLI supports the following sandbox and execution flags:

*   **`--sandbox`**: Turns the sandbox on for the session, overriding `settings.json`.
*   **`--mode=auto`**: Runs commands inside the sandbox by default and automatically checks commands that need to run outside the sandbox so safe, reversible commands proceed without prompting.

#### If the sandbox isn’t available

Starting in `v1.4.4`, the following applies if the sandbox isn’t available on your machine (for example, on Windows 10, earlier Windows 11 builds, or Linux hosts and some containers that block unprivileged user namespaces):

*   `enableTerminalSandbox` and `--sandbox` have no effect.
*   `proceed-in-sandbox` behaves like `request-review`.
*   `auto` mode isn’t offered.
*   `/config` hides **Sandbox Mode**, `proceed-in-sandbox`, and `auto`.

Your saved settings aren’t changed, so they take effect once the sandbox is available.

### CLI permissions integration

The sandbox derives its access boundaries from your **[Permissions](/docs/permissions)** configuration:

*   **Filesystem**: Workspace folders and paths allowed under `write_file` are mounted read-write. Paths allowed under `read_file` are mounted read-only, on top of the default system mounts. Denied paths are blocked, and everything else is inaccessible, except that on Windows, folders outside your user profile stay readable.
*   **Network**: Sandboxed commands run without network access by default. Domains allowed under `read_url` are added to the sandbox’s outbound allowlist.
*   **Commands outside the sandbox**: A `command` allow rule lets a matching command run without prompting, inside or outside the sandbox. This is useful for tools that can’t work inside the isolation boundary, such as Docker or commands that talk to system services. Business and enterprise accounts use an `unsandboxed` allow rule for this instead.

The agent can also request to run a command outside the sandbox on its own—for example, to retry a command that failed due to sandbox restrictions. On Windows, this includes some package installs and commands that connect to servers running outside the sandbox. How Antigravity CLI handles these requests depends on your mode:

*   **`auto` mode** (`v1.3.5+` on macOS and Linux, `v1.4.4+` on Windows): Antigravity CLI automatically evaluates commands that need to run outside the sandbox so safe, reversible commands run without prompting while irreversible commands still prompt for confirmation.
*   **Modes other than `auto`**: These requests always require your approval unless the command matches a `command` allow rule (an `unsandboxed` allow rule for business and enterprise accounts).

#### Example

The following example configures sandbox allow and deny rules in `settings.json`:

```json
{
    "permissions": {
        "allow": [
            "command(npm test)",
            "command(git diff)",
            "command(git push)",
            "read_file(/var/log/app)",
            "write_file(src/)"
        ],
        "deny": [
            "command(rm -rf /)",
            "command(sudo *)",
            "write_file(/home/user/.ssh)"
        ]
    }
}
```

With this configuration:

*   `npm test` and `git diff` run inside the sandbox.
*   `git push` runs without prompting, even when it needs to run outside the sandbox, through `command(git push)`.
*   `rm -rf /` and `sudo` are always blocked.

### Interactive prompts

When a command needs review, you can approve it once or turn the approval into a standing rule:

```text
Do you want to proceed?
1. Yes
2. Yes, and always allow in this conversation for commands that start with 'npm test'
3. Yes, and always allow for commands that start with 'npm test' (Persist to settings.json)
4. No
```

For business and enterprise accounts, when the agent asks to bypass the sandbox, the prompt calls it out explicitly so you can judge the risk:

```text
🔓 Allow sandbox bypass for command execution?
⚠️ Confirm the command is safe to run outside of the sandbox with full network and disk access.
```

Approving “always allow” here records an `unsandboxed(...)` rule instead of a plain `command(...)` rule.

For other accounts, these requests use the standard command prompt, and “always allow” records a `command(...)` rule.

## Related resources

Explore related documentation and guides:

*   **[Agent permissions](/docs/permissions)**: Configure allow, deny, and ask rules.
*   **[Agent settings](/docs/agent-settings)**: Command execution policies and file access controls.
*   **[Settings](/docs/settings)**: Global application and CLI preferences.
*   **[Projects](/docs/projects)**: Multi-folder configuration and per-project settings.