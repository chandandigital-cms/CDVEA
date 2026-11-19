# Set up CDVEA on Windows

Use Extract All, open the extracted `CDVEA` folder and double-click `Install-CDVEA.cmd`. Setup checks the bundled tools and speech model. It also registers the plugin with Codex and Claude Code when their commands are on PATH, the list of folders Windows checks for installed commands. Restart your host and start a new chat after registration.

To use the local tools on their own, double-click `CDVEA.cmd` and type a command in the window it opens:

```bat
CDVEA.cmd doctor
CDVEA.cmd catalog
CDVEA.cmd init "D:\VideoJobs\my-edit"
CDVEA.cmd transcribe "D:\Videos\interview.mp4" --language bn
```

From a terminal, run `Install-CDVEA.cmd --hosts none` for the local check alone. Use `--hosts codex` or `--hosts claude` to register one host. The [Codex](https://developers.openai.com/codex/quickstart) and [Claude Code](https://code.claude.com/docs/en/setup) setup pages cover their own apps and sign-in.

Keep your media in a separate working folder and keep the extracted CDVEA files together. If you move CDVEA after registering it, rerun setup from the new folder. The [capability list](CAPABILITIES.md) shows the features that need extra software.
