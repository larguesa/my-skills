# Antigravity features

Available on: Antigravity App, Antigravity CLI

The Antigravity App and the Antigravity CLI run the same agent, so most features work on both. This page starts with the features they share, and then covers the features that are specific to the [Antigravity App](#antigravity-app-features) and the [Antigravity CLI](#antigravity-cli-features).

## Features in the App and CLI

Where a feature works differently in the App and the CLI, select your surface in the tabs. Your choice applies to every tab on this page and is remembered across the docs.

### Projects

Agents work in **projects**, which define the folders an agent can access and the settings and permissions it uses.

### Antigravity App

*   **Worktree support**: Projects natively support Git worktrees, allowing agents to operate in isolated background folders.
*   **Scoped settings**: Settings are scoped, allowing you to have different security settings per project. This means you can have a more permissive setting for a trusted project and a more restrictive security setting for an untrusted folder. For the available presets, refer to [Permission presets](/docs/permissions#permission-presets).
*   **Scoped permissions**: Attach permission grants to projects to control what the agents are allowed to access. Permissions manually granted during a conversation can persist, allowing the agent to learn trusted actions over time.
*   **Multi-folder access**: You can configure a project to work in multiple folders, allowing agents to operate across different codebases within the same conversation.

### Antigravity CLI

*   **Default project**: Conversations run in the `default-cli-project` unless you start the CLI with `--project=<project_id>` or `--new-project`.
*   **Resumed conversations**: When you resume a conversation with `/resume` or `--conversation`, the CLI uses that conversation’s project.
*   **Fork a conversation**: Run `/fork <project_id>` to continue a copy of the current conversation in another project.

[Learn more about projects](/docs/projects).

### Secure by default

By default, agents ask before sensitive actions and limit their file access to your project’s folders. The details differ by surface:

### Antigravity App

*   **Interactive approvals**: By default, commands run inside the isolated [Terminal sandbox](/docs/sandbox) without prompting, and agents request your explicit permission before running terminal commands outside it. Under the **Auto** preset, commands outside the sandbox are evaluated automatically so safe, reversible commands proceed while risky or irreversible actions ask for your approval. With the [previous permission settings](/docs/agent-settings#previous-permission-settings), agents ask before running any terminal command.
*   **Bounded access**: By default, your agent can only read and write within the provided folders of a project. If you broaden your permission settings (for example, by choosing the **Turbo** preset), the agent has read and write access over your full machine.

### Antigravity CLI

*   **Interactive approvals**: The default `request-review` permission asks before the agent writes files, runs shell commands, or uses web tools, unless one of your allow rules matches. In [`auto` mode](/docs/cli/modes), the CLI approves workspace file edits, runs shell commands inside the [terminal sandbox](/docs/sandbox), and evaluates commands outside the sandbox so only risky or irreversible actions ask for your approval.
*   **Terminal sandbox**: The [terminal sandbox](/docs/sandbox) is off by default. Turn it on with `enableTerminalSandbox` in `settings.json` or the `--sandbox` flag. `auto` mode turns it on automatically.
*   **Files outside your workspace**: The agent asks before it reads or edits files outside your workspace folders. To treat those files like workspace files, turn on `allowNonWorkspaceAccess`.

[Learn more about permissions](/docs/permissions) and [the terminal sandbox](/docs/sandbox).

### Subagents

The main agent can delegate work, such as research, builds, or test runs, to subagents. Each subagent starts with a clean context and runs in its own conversation, in parallel with your main conversation.

### Antigravity App

In the side panel’s **Overview**, open **Subagents** and select a subagent to follow its conversation.

### Antigravity CLI

*   **Monitor and approve**: Open the `/agents` panel to monitor subagents and approve their requests.
*   **Jump to approvals**: Press Alt+J to jump to the next subagent that’s waiting for approval.
*   **Approve in place**: Press Ctrl+K to approve a pending request without leaving the main conversation.

[Learn more about subagents](/docs/subagents).

### Browser subagent

The browser subagent drives Google Chrome to test and debug web pages:

*   **On-demand**: Invoke the browser subagent through the [`/browser` command](/docs/commands/browser).
*   **Chrome DevTools integration**: Integrate natively with Chrome DevTools MCP.
*   **Video recording**: Can record the subagent’s actions as a WebM video when it interacts with a page.

### Slash commands

Type `/` in the App’s message box or the CLI’s prompt box to run commands such as [`/plan`](/docs/plan), [`/grill-me`](/docs/commands/grill-me), [`/goal`](/docs/commands/goal), [`/boost`](/docs/boost), [`/schedule`](/docs/commands/schedule), and [`/teamwork`](/docs/teamwork). Some commands are available on only one surface, and `/boost` and `/teamwork` require a paid plan.

[Browse all slash commands](/docs/slash-commands).

### Mentions and quoting

Point the agent at the right context so it doesn’t have to search for it.

### Antigravity App

Type `@` in the message box to mention files, folders, rules, and past conversations, or select text in a response, file, diff, or artifact and click **Quote** to add it to your next message.

### Antigravity CLI

Type `@` in the prompt box to mention files and directories, or start your prompt with `@` and a subagent’s name to send that subagent a message.

[Learn more about mentions and quoting](/docs/at-mentions).

### Voice transcription

Antigravity features built-in live voice transcription, allowing you to prompt agents and leave feedback using natural speech.

### Antigravity App

*   **Start or stop**: Click the microphone button next to the message box to start recording, and click it again to stop. You can also press Ctrl+M to start recording, and press it again to stop.
*   **Live view**: As you speak, your words are transcribed in real time directly into the message box.
*   **Conversational awareness**: Antigravity gives the speech recognizer your recent conversation and the text around your cursor, so project-specific terms are more likely to come through correctly.
*   **Where it works**: Use voice in the message box to start conversations and send prompt updates, and in artifact comments to leave precise, inline feedback on plans, code diffs, and deliverables.
*   **Talk with the agent**: To have a spoken, two-way conversation with the agent instead of dictating, use [voice mode](/docs/voice-mode).

### Antigravity CLI

*   **Talk with the agent**: Run `/voice live` or press F6 to start [voice mode](/docs/voice-mode), a spoken, two-way conversation with the agent.
*   **Start dictation**: Run `/voice dictate` or `/record`, or press F5. Your words appear in the prompt box, where you can edit them before you send.
*   **Dictate over SSH**: When the CLI runs on a remote machine, run `agy mic-serve` on your local machine to stream your microphone to it.
*   **Availability**: Voice dictation in the CLI isn’t currently available for business or enterprise accounts.

[Learn more about voice dictation in the CLI](/docs/cli/commands/voice).

### Remote Control

Remote Control allows you to drive and monitor your Antigravity App sessions and Antigravity CLI instances across multiple machines from any web browser:

*   **Work from any device**: Start long-running agent work on your workstation, and then monitor it or approve actions from a phone or laptop.
*   **Keep your local setup**: Agents keep full access to your workstation’s files, toolchains, credentials, and Git worktrees, without a separate environment.
*   **Get notified**: Receive browser push notifications when tasks complete or when your input is needed.

To turn on Remote Control:

### Antigravity App

In **Settings**, open **Application** and turn on **Enable Remote Control**. You can then enter a **Device Name** to identify the machine.

### Antigravity CLI

*   **Current session**: Run `/remote-control` to turn on Remote Control for the active terminal session, and `/remote-control off` to turn it off.
*   **New session**: Start the CLI with the `--remote-control` flag.
*   **Always-on machine**: Run `agy remote-control start` to keep a headless CLI instance available in the background.

[Learn more about Remote Control](/docs/remote-control).

### Remote Agents

Remote Agents run your agent sessions and tools in an isolated, Google-managed remote environment so tasks continue executing even when your local machine is asleep or offline:

*   **Remote workspaces and resources**: Create remote projects connected to GitHub repositories, Google Drive files, and uploaded files.
*   **Access from anywhere**: Start and monitor remote conversations from the Antigravity App, the Antigravity CLI, or any desktop or mobile browser at [antigravity.google.com](https://antigravity.google.com).
*   **Availability**: Available to **Google AI Pro** and **Google AI Ultra** subscribers signed in with a personal Google Account.

To start a remote conversation:

### Antigravity App

In the left sidebar, click **+** next to **Projects** and select **New Remote Project**, or open [antigravity.google.com](https://antigravity.google.com) in any browser.

### Antigravity CLI

Start the CLI with the `--remote-agent` flag. Add `--project` to open a specific remote project, and run `/projects` to create remote projects and attach resources.

[Learn more about Remote Agents](/docs/remote-agents).

### Skills, rules, and MCP servers

Extend what the agent knows and can do. These customizations work in both the App and the CLI:

*   **[Skills](/docs/skills)**: Give the agent folders of instructions, each with a `SKILL.md` file, that it follows when working on specific tasks.
*   **[Rules](/docs/rules)**: Set persistent instructions, coding standards, and architectural constraints that apply to every conversation.
*   **[MCP servers](/docs/mcp)**: Connect the agent to local developer tools, databases, and remote APIs through the Model Context Protocol.

### JSON hooks

JSON hooks allow you to execute custom local shell scripts at critical stages of an Antigravity agent’s execution cycle. You can intercept and control the agent’s behavior before tool calls, after model responses, or at loop stopping conditions—configured globally or per workspace using simple JSON files.

[Learn more about hooks](/docs/hooks).

### Plugins

Plugins are namespaced bundles that can contain skills, agents, rules, MCP servers, and hooks as a single deployable unit.

### Antigravity App

In the left sidebar, click **Customizations**, and then open the **Marketplace** tab to browse and install plugins. Plugins that you install in the App also appear in the CLI.

### Antigravity CLI

*   **Plugin manager**: Run `/plugin` to open the plugin manager, and press Tab to switch between the **Installed** and **Discover** tabs.
*   **From your shell**: Run `agy plugin install <plugin-name>` to install a plugin, and use `agy plugin list`, `enable`, `disable`, and `uninstall` to manage your plugins.

[Learn more about plugins](/docs/plugins) and [the Marketplace](/docs/marketplace).

## Antigravity App features

These features are specific to the Antigravity App.

### Conversations outside of projects

Start quick, one-off conversations outside of any project. These sessions run in a local scratch folder. They have their own settings and permissions in addition to inheriting from global permissions.

### Search and command palette

Press Cmd+K (macOS) or Ctrl+K (Windows and Linux) to search past conversations by title, project, and full text, including your prompts and the agent’s responses. The same command palette also finds files in your project, runs app commands, and starts a conversation in another project.

[Learn more about search and the command palette](/docs/search).

### Side panel and Overview panel

Open artifacts, files, diffs, terminals, subagent conversations, and web pages as tabs in the side panel, next to your conversation. The **Overview** panel at the top right of each conversation lists the changes, artifacts, subagents, and links that the conversation produced, so you can open any of them in one click. To work in two conversations at once, split the window.

[Learn more about the side panel and the Overview panel](/docs/side-panel).

### Voice mode

Talk with the agent out loud, and hear it answer in real time. With voice mode in Antigravity, enabled by **Gemini Live**, click **Start Voice mode** in an empty message box to start a spoken conversation in which you can do the following:

*   **Give and steer tasks**: Ask for work, add details or corrections while the agent works, or tell it to stop.
*   **Answer by voice**: Allow or deny permission prompts and answer the agent’s questions without clicking. Destructive actions still need a click on screen.
*   **Hear progress when you want it**: The agent works quietly by default. Ask it to keep you posted, and how often.

[Learn more about voice mode](/docs/voice-mode).

### Automations

Automations (previously called scheduled tasks) let you plan ahead with your projects by sending messages to your agents on a schedule, even while you’re away. Open them from **Automations** in the left sidebar:

*   **Repeatable**: Set up time-based triggers to start conversations periodically.
*   **Model tier**: Each automation runs on the model tier you choose: Flash Lite, Flash (the default), or Pro.
*   **Approximate timing**: Runs start close to their scheduled time rather than on the exact minute. Antigravity spreads them out by up to 10% of the interval, and by no more than 15 minutes.
*   **Run on demand**: Run an automation right away with **Run Now** from its menu, or select **Create with Prompt** to have the agent walk you through setting up a new one.

For a timer or recurring check inside a single conversation, in either the App or the CLI, use the [`/schedule` command](/docs/commands/schedule).

### Built-in browser

Use the built-in browser to check your running app or read documentation in the side panel, next to your conversation, and to point the agent to exactly what you see on a page.

![The Antigravity App with a conversation on the left, where the agent summarizes the Gemini 4 Argon announcement and links to it, and the built-in browser in the side panel on the right showing that blog post on antigravity.google with its hero image](/assets/image/docs/browser/built-in-browser.png)

*   **Open a page**: Click a web link in an agent response. To open a new browser tab, press Cmd+T (macOS) or Ctrl+T (Windows and Linux), or click **+** in the side panel, and then choose **Browser**. To open a link in your default browser instead, hold Cmd (macOS) or Ctrl (Windows and Linux) while you click it.
*   **Go to a URL or search**: Type in the address bar. For local servers that don’t use HTTPS, include `http://`, for example `http://localhost:3000`.
*   **Navigate**: Use **Back**, **Forward**, and **Reload** in the toolbar, or click **Open in external browser** to open the current page in your default browser. Right-click a link to open it in a new tab or in your external browser.
*   **Keep sign-ins separate**: The built-in browser keeps its own cookies and sign-ins, separate from your Chrome profile.

To point the agent to part of a page, select text and click **Comment** (C) to leave feedback, or **Quote** (Cmd+L on macOS, Ctrl+L on Windows and Linux) to add the text to your message. The agent receives the page URL and the selected text with your next message.

![Text selected on a web page in the built-in browser, with a popup that offers Comment C and Quote ⌘L](/assets/image/docs/browser/built-in-browser-comment.png)

To have the agent browse and test pages for you, use the [`/browser` command](/docs/commands/browser), which runs the browser subagent in Google Chrome.

### PDF viewer

PDF files open in the side panel, so you can read a spec or paper next to your conversation and point the agent to specific passages. To open a PDF from your project, click it in an agent response, or click **+** in the side panel, choose **Open File**, and search for the PDF. Links to PDFs on the web open in the built-in browser.

![A Bookmarks API guide PDF open in the side panel of the Antigravity App, with a toolbar at the bottom for page thumbnails, page navigation, zoom, and fit mode](/assets/image/docs/pdf/pdf-viewer.png)

*   **Navigate**: Use the toolbar at the bottom of the PDF to show page thumbnails, change pages, zoom, and fit the page or the width. To search the PDF, download it, or copy its path, use the **More actions** menu at the top.
*   **Comment or quote**: Select text and click **Comment** (C) or **Quote** (Cmd+L on macOS, Ctrl+L on Windows and Linux), the same as on a web page.

### Jupyter notebooks

Open `.ipynb` files in the side panel to view rendered Markdown cells, syntax-highlighted code cells with execution counts, and inline text, image, and error outputs. Use the **Preview** / **Raw** toggle in the header to inspect the underlying JSON, or add inline comments on cells to send feedback to the agent.

[Learn more about Jupyter notebooks](/docs/jupyter-notebooks).

### Integrated terminal

Open a terminal in the side panel: click **+** and choose **Terminal**. To show or hide the terminal at any time, press Cmd+J (macOS) or Ctrl+J (Windows and Linux).

### Version control system (VCS) panel

The Antigravity App provides a Git-native **Review** pane for the changes in your project. Open it from any conversation by clicking **Review** () in the **Overview** panel, and then perform the following actions:

*   **Compare views**:
    *   **Uncommitted**: View all staged and unstaged working tree changes.
    *   **Branch**: Review all changes made on the current branch.
    *   **Agent Edits**: Inspect the files that the agent modified in the conversation.
*   **File actions**: Stage, unstage, or discard unstaged changes per file.
*   **Repo actions**:
    *   **Commit**: Create local commits, with a generated commit message if you leave the message empty.
    *   **Amend**: Add changes to the latest commit.
    *   **Push**: Send branch commits to a remote repository.
*   **Feedback**: Comment on lines in a diff to send feedback to the agent.

[Learn more about reviewing changes](/docs/review-changes).

## Antigravity CLI features

These features are specific to the Antigravity CLI.

### Terminal UI and commands

Run `agy` to work with the agent in an interactive terminal UI. Besides the shared slash commands, the CLI has commands for managing your session, such as `/resume`, `/rewind`, `/model`, `/context`, `/codesearch`, `/tasks`, and `/usage`.

*   **Keyboard shortcuts**: Customize shortcuts with `/keybindings`, or edit prompts with modal Vim keybindings in [Vim editor mode](/docs/cli/vim-editor-mode).
*   **Execution modes**: [Choose an execution mode](/docs/cli/modes) to control whether the CLI pauses to ask before it modifies files or runs commands.

[Browse all CLI commands](/docs/cli/reference).

### Review changes with `/diff`

Run `/diff` to open the interactive diff viewer, where you can inspect workspace changes, commit history, and the changes from each agent turn, and add line-by-line comments to steer the agent’s next steps.

[Learn more about the diff viewer](/docs/cli/commands/diff).

### Headless mode

Run the CLI non-interactively to script agent tasks, integrate with CI pipelines, and capture machine-readable output. Pass a prompt with `-p` (or its aliases `--print` and `--prompt`) to run it once and exit.

[Learn more about headless mode](/docs/cli/headless).

### Customize with `settings.json`

Configure the CLI in `~/.gemini/antigravity-cli/settings.json`. For example, in addition to your permission mode, you can define specific commands that the agent is allowed or denied to run:

```json
{
  "permissions": {
    "allow": ["command(git)", "command(npm test)"],
    "deny": ["command(rm -rf)"]
  }
}
```

You can also pipe live agent metadata (JSON that contains the current working directory, active model, token usage, state, and more) into your own shell scripts to generate a custom [status line](/docs/cli/statusline) or [terminal window title](/docs/cli/title).

[Learn more about CLI settings](/docs/settings?tab=cli).