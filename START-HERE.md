# CDVEA by Chandan Digital

This folder contains the final source code for manual GitHub upload.

## Upload the source

Open your private GitHub repository. Use Add file, then Upload files. Upload the contents of this folder at the repository root, including the dot-prefixed plugin folders and configuration files. Keep the existing directory structure. If your browser rejects a large group, use smaller batches or a desktop Git client.

The README.md, setup.py, setup.ps1, skills, scripts, mcp and vendor folders belong directly at the repository root. Do not add an extra CDVEA-FINAL directory level around them.

The ZIP is a copy for storage and transfer. Uploading only the ZIP stores an archive; it does not unpack the source into the repository.

## Set up another Windows device

Follow SETUP-GUIDE.md. After installing the prerequisites, run setup.ps1 once. It prepares the local model and runtime and registers the plugin with the host CLIs it finds. Restart the host once, then give normal video editing instructions.

The source package has 30 skills, 8 agent definitions, 9 commands and 49 MCP tools. Model weights, virtual environments and installed applications are intentionally separate; the setup script downloads them. Account credentials are not included.

Keep the upstream licence files and THIRD-PARTY-NOTICES.md when distributing this code.
