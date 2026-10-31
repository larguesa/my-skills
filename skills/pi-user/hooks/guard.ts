// pi extension: blocks risky tool calls (git push, mutating curl, secrets access, rm -rf /).
// Load with: pi -e <skilldir>/hooks/guard.ts ...
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const BASH = /git\s+push|curl .*-X *(POST|PUT|DELETE|PATCH)|\.secrets|\.env\b|rm -rf \/(\s|$)/;
const PATH = /(^|\/)(\.secrets|\.env)(\/|$)|auth\.json$/;

export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event) => {
    const input: any = event.input ?? {};
    if (event.toolName === "bash" && BASH.test(String(input.command ?? ""))) {
      return { block: true, reason: "Blocked by guard: needs the owner's explicit OK" };
    }
    const p = String(input.path ?? input.file_path ?? "");
    if (["read", "write", "edit"].includes(event.toolName) && PATH.test(p)) {
      return { block: true, reason: "Blocked by guard: secrets/credentials path" };
    }
  });
}
