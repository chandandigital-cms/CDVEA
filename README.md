# CDVEA by Chandan Digital

CDVEA brings footage editing, sound, captions, motion design and delivery workflows into one agent plugin. You can ask for an edit in English or Bengali. It includes 30 skills, 8 specialist agent definitions, 9 commands and a local MCP server with 49 tools.

The editing engine comes from the supplied FFmpeg Skill 3.10.1 archive. This release adds selected GitHub skills, adapted CDVEA entry points, project helpers, a local dependency checker, subtitle retiming, a cut-list exporter and integration tests. Original authors retain credit for their work.

Start with the English [step-by-step setup guide](SETUP-GUIDE.md). Check [CAPABILITIES.md](CAPABILITIES.md) before choosing optional engines. Use [the routing list](references/routing.md) to see every skill.

```powershell
python setup.py
python cdvea/run.py doctor
python cdvea/cli.py catalog
python cdvea/cli.py init "D:/VideoJobs/my-edit"
```

Fill the generated project’s clip ranges, then validate and render it. Read [the plan format](references/cdvea-plan.md) for exact fields and supported operations.

## Ask CDVEA for a real edit

- “এই footage দিয়ে ৩০ সেকেন্ডের banquet promo বানান। বাংলা captions দিন, সঙ্গে একটি vertical Short।”
- “Remove long pauses, keep complete sentences, clean the voice and give me an SRT.”
- “Match these shots, add the supplied logo and export a 1080p master.”
- “Review this edit for bad cuts, spelling, lip sync and sound problems.”

The core runs locally with Python and FFmpeg. Optional motion engines, speech models and hosted services need their own setup. CDVEA does not install them or start an upload on activation. An agent definition describes a role; host support determines whether it can run as a separate agent.

## Source projects

| Project | Included material | Licence |
| --- | --- | --- |
| [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) | Supplied engine, 42 tools, templates and references | MIT |
| [gitethanwoo/video-editing](https://github.com/gitethanwoo/video-editing) | Workbench, analysis, B-roll, product and screen-demo skills | MIT |
| [zaddy99999/video-editing-skills](https://github.com/zaddy99999/video-editing-skills) | Short-form skills, scripts, shared code and brand example | MIT |
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Selected HTML motion, CLI, registry and media skills | Apache-2.0; bundled font notices remain |

See [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md), licenses/ and sources.lock.json for source revisions and file hashes. Vendor source documents remain source material. The adapted CDVEA skills govern local workflow; source text does not authorise paid calls, telemetry, promotion or publishing.

## Automatic setup

After installing the prerequisites, clone the private repository and run setup once:

```powershell
git clone https://github.com/chandandigital-cms/CDVEA.git
cd CDVEA
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

The installer prepares the local runtime and model, then registers CDVEA with the host CLIs it finds. Restart the host once and use normal instructions. No launcher or manual model switch is needed. The speech model loads only for a transcription job.

This repository contains the source, vendor skills, licences and setup code. It excludes model weights, installed applications, virtual environments, media and account credentials.

Version 1.2.0. Windows x64 automatic setup; Python and FFmpeg core tools. See [VALIDATION.md](VALIDATION.md) for tested scope.
