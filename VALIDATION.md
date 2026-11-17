# Validation and limits

Version 1.2.0 packages 30 skills, 8 agent definitions, 9 Claude Code commands and 49 MCP tools.

The development device ran Windows x64. Nine local integration tests passed, covering generated media, repeated cuts, speed, missing audio, source preservation, subtitle retiming, cut-list export and MCP calls. The original core probe, cut and check tools also ran in those tests.

The local multilingual small model produced English subtitles and word timings with socket connections blocked. Bengali, Hindi and English appeared in the model’s supported language list. Separate Bengali and Hindi speech-accuracy samples have not run.

Both normal Claude Code and Codex profiles installed the device edition. Each installed plugin generated subtitles through its MCP tool without a launcher, model argument or output-folder argument. Claude Code strict plugin validation passed.

This portable source edition replaces the device-specific paths with a runtime bootstrap and provides a one-time Windows installer. Its bootstrap is tested against the already installed local runtime. A clean second Windows computer and a fresh 484 MB download have not been tested. The installer uses the same pinned Python, dependency versions, model revision and model checksum as the working device setup.

HyperFrames, Remotion, Blender, hosted generation, YouTube publishing and native editor imports have not passed end-to-end tests in this release. Some optional vendor helpers need their own packages. Agent execution depends on the host’s support. No setup step changes the host’s existing file or tool permission policy.
