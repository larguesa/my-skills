// Direct tool-call tripwire. No command is executed; unknown tools need separate restriction.
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { posix } from "node:path";

function sensitive(value: string): boolean {
  return value.replaceAll("\\", "/").toLowerCase().split("/").some(p =>
    [".secrets", ".ssh", "auth.json", ".credentials.json", "credentials.json", "id_rsa", "id_ed25519"].includes(p) ||
    ((p === ".env" || p.startsWith(".env.")) && p !== ".env.example"));
}

function protectedRemoval(value: string): boolean {
  const p = value.replaceAll("\\", "/").replace(/\/+$/, "").toLowerCase() || "/";
  const literals = ["/", "/*", "/**", "~", "~/*", "$home", "$home/*", "${home}", "${home}/*", "/home", "/home/*", "/users", "/users/*"];
  if (literals.includes(p) || /^[a-z]:\/?\*?$/.test(p) || /^(?:[a-z]:)?\/(?:home|users)\/[^/]+(?:\/\*)?$/.test(p)) return true;
  const normalized = posix.normalize(p.replace(/\*$/, "").replace(/\/+$/, "") || "/");
  const home = (process.env.HOME ?? process.env.USERPROFILE ?? "").replaceAll("\\", "/").replace(/\/+$/, "").toLowerCase();
  return normalized === "/" || Boolean(home && normalized === home);
}

function simpleCommands(command: string, powershell: boolean): string[] {
  const parts: string[] = [];
  let start = 0, quote = "", escaped = false;
  for (let i = 0; i < command.length; i++) {
    const char = command[i];
    if (escaped) escaped = false;
    else if (char === (powershell ? "`" : "\\") && quote !== "'") escaped = true;
    else if (quote) {
      if (char === quote) quote = "";
    } else if (char === '"' || char === "'") quote = char;
    else if (char === "&" && (command[i - 1] === "<" || command[i - 1] === ">" || command[i + 1] === ">")) continue; // Redirection, not a command boundary.
    else if (";&|()\n".includes(char)) {
      parts.push(command.slice(start, i));
      start = i + 1;
    }
  }
  if (quote) throw new Error("unbalanced quotes");
  parts.push(command.slice(start));
  return parts;
}

function words(command: string): string[] {
  const parts = command.match(/"[^"\n]*"|'[^'\n]*'|[^\s;&|()]+/g) ?? [];
  return parts.map(p => {
    if (p.startsWith('"') || p.startsWith("'")) {
      if (p.length < 2 || p.at(-1) !== p[0]) throw new Error("unbalanced quotes");
      return p.slice(1, -1);
    }
    return p;
  });
}

function gitVerb(tokens: string[], index: number): string {
  let i = index + 1;
  while (i < tokens.length) {
    if (["-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env"].includes(tokens[i])) i += 2;
    else if (tokens[i].startsWith("-")) i++;
    else return tokens[i];
  }
  return "";
}

function commandReason(command: string, powershell: boolean): string | undefined {
  const normalized = command.replace(/\\\r?\n|`\r?\n/g, "");
  for (const statement of simpleCommands(normalized, powershell)) {
    const tokens = words(statement);
    for (let i = 0; i < tokens.length; i++) {
      const name = tokens[i].replaceAll("\\", "/").split("/").at(-1) ?? "";
      const gitName = powershell ? name.toLowerCase().replace(/\.exe$/, "") : name;
      const tail = tokens.slice(i + 1);
      if (sensitive(tokens[i])) return "credential or secrets path";
      if (gitName === "git" && ["push", "remote", "config"].includes(gitVerb(tokens, i))) return "git publication or configuration";
      if (["vercel", "netlify", "wrangler", "flyctl", "kubectl", "terraform", "sudo", "su"].includes(name)) return "deployment or elevated authority";
      if (["npm", "pnpm", "yarn", "cargo", "uv"].includes(name) && tail.includes("publish")) return "package publication";
      if (name === "twine" && tail.includes("upload")) return "package publication";
      if (name === "gh" && (tail[0] === "api" || tail[0] === "secret" || ["pr", "issue", "release", "repo"].includes(tail[0]) && tail.slice(1).some(x => ["create", "edit", "delete", "close", "reopen", "merge", "comment", "upload", "publish", "fork", "rename", "set"].includes(x)))) return "GitHub mutation";
      if (name === "curl") {
        for (let j = 0; j < tail.length; j++) {
          const a = tail[j], next = tail[j + 1] ?? "";
          if (["-X", "--request"].includes(a) && !["GET", "HEAD", "OPTIONS"].includes(next.toUpperCase())) return "mutating HTTP request";
          if (a.startsWith("-X") && a.length > 2 && !["GET", "HEAD", "OPTIONS"].includes(a.slice(2).toUpperCase())) return "mutating HTTP request";
          if (a.startsWith("--request=") && !["GET", "HEAD", "OPTIONS"].includes(a.slice(10).toUpperCase())) return "mutating HTTP request";
          if (["-d", "-F", "-T"].includes(a) || /^--(?:data|json|form|upload-file)/.test(a) || /^-[dFT].+/.test(a)) return "HTTP upload or body";
        }
      }
      if (["rm", "Remove-Item", "remove-item", "ri"].includes(name)) {
        const recursive = tail.some(a => a.startsWith("-") && (a.replace(/^-+/, "").includes("r") || ["--recursive", "-recurse"].includes(a.toLowerCase())));
        const force = tail.some(a => a.startsWith("-") && (a.replace(/^-+/, "").includes("f") || ["--force", "-force"].includes(a.toLowerCase())));
        if (recursive && force && tail.some(a => !a.startsWith("-") && protectedRemoval(a))) return "protected root or home removal";
      }
    }
  }
  return undefined;
}

export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event: any) => {
    const block = (reason: string) => ({ block: true, reason: "Blocked by guard: " + reason });
    try {
      if (!event || typeof event !== "object" || typeof event.toolName !== "string" || !event.input || typeof event.input !== "object" || Array.isArray(event.input)) return block("malformed tool call");
      if (["bash", "powershell"].includes(event.toolName)) {
        const cmd = event.input.command;
        if (typeof cmd !== "string" || !cmd.trim() || cmd.includes("\0")) return block("malformed command");
        const reason = commandReason(cmd, event.toolName === "powershell");
        return reason ? block(reason) : undefined;
      }
      if (["read", "write", "edit", "grep", "find", "ls"].includes(event.toolName)) {
        const fallback = ["grep", "find", "ls"].includes(event.toolName) ? "." : undefined;
        const path = event.input.path ?? event.input.file_path ?? fallback;
        if (typeof path !== "string" || !path.trim() || path.includes("\0")) return block("malformed file path");
        return sensitive(path) ? block("credential or secrets path") : undefined;
      }
      return undefined;
    } catch {
      return block("unreadable or malformed tool input");
    }
  });
}
