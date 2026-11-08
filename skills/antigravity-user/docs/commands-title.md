# Window title command (/title)

Available on: Antigravity CLI

Configure dynamic terminal window titles interactively.

## Overview

The `/title` command allows you to toggle the terminal window title feature on and off, or set its state explicitly. When enabled, the terminal title bar dynamically updates to show the active model, workspace, and agent state.

For details on how to write custom scripts to format the window title, refer to the conceptual **[Terminal title customization guide](/docs/cli/title)**.

## Interactive toggling

You can control the window title feature by running the `/title` command.

To toggle the feature on and off, run the following command:

```text
/title
```

To enable it explicitly, run the following command:

```text
/title on
```

To disable it explicitly, run the following command:

```text
/title off
```

## Next steps

Explore the following guides to further customize your terminal display:

*   **[Terminal title guide](/docs/cli/title)**: Learn how to write custom scripts to format the window title.
*   **[Status line command](/docs/cli/commands/statusline)**: Customize your TUI status line.
*   **[CLI reference](/docs/cli/reference)**: View all available slash commands.