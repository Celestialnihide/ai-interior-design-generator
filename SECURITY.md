# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.6.x   | yes       |
| 0.5.x   | security fixes only |
| < 0.5   | no        |

## Reporting a vulnerability

Email `security@ai-interior-design-generator.dev` with a description, repro steps, and the affected version. We acknowledge within 72 hours and aim to patch critical issues within 14 days.

Please do not open public issues for security problems.

## Threat model

`ai-interior-design-generator` is a **local desktop tool**. It runs on the user's machine, loads plugins from disk, and may call a user-configured model backend. The relevant attack surface:

- **Plugin loading.** Plugins execute arbitrary Python. Only install plugins you trust. The loader sandboxes imports into a restricted namespace but does **not** provide a security boundary — treat `plugins/` like a shell script directory.
- **Model files.** ONNX / safetensors files are parsed by third-party runtimes. Keep ONNX Runtime patched.
- **Project files.** `.iidproj` files are JSON with embedded asset references. Paths are validated against the project root; absolute paths and `..` traversal are rejected.
- **Remote backends.** If you point the app at a hosted inference endpoint, your prompts and room photos leave the machine. The app warns on first configuration.
- **Update channel.** Auto-update is disabled by default. When enabled, it verifies a signed manifest (Ed25519) before applying.

## What we consider in scope

- Path traversal via `.iidproj` or plugin manifests.
- Code execution from a malicious plugin **that bypasses the documented trust model** (i.e. a plugin that claims to be data-only but executes).
- Signature bypass in the updater.
- Crash / DoS from malformed model or image input.

## Out of scope

- Vulnerabilities in user-installed plugins.
- Issues that require an attacker to already have local code execution.
- GPU driver bugs.

## Hardening checklist for users

- Run with a standard (non-admin) Windows account.
- Keep plugins under version control and review diffs.
- Leave auto-update on the signed channel.
- Store API keys in the OS credential vault, not in `config/local.toml`.