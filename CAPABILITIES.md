# What CDVEA can do

This release packages 30 discoverable skills, 8 specialist agent definitions, 9 Claude Code commands and 49 MCP tools. The MCP surface contains the original 42 FFmpeg tools and 6 project tools and an automatic local transcription tool. Optional engines keep their own setup and terms.

| Work | Included route | What you need |
| --- | --- | --- |
| Cut, join, trim, speed ramps, freeze, reverse, loops | Original FFmpeg scripts | FFmpeg and Python |
| Reproducible clip assembly and speed changes | cdvea/cli.py | FFmpeg with libx264 and AAC |
| Multi-track composites and custom filter graphs | Workbench skill and scripts | FFmpeg; optional Remotion |
| Crop, rotate, 360 view, grid, B-roll, picture-in-picture | Original scripts | Required filters in your FFmpeg build |
| Multicam and external-audio sync | sync.py and multicam.py | Sources with useful sync evidence |
| Colour correction, LUT, HDR to SDR | color.py and colour workflow | Correct source profile and supported filters |
| Stabilisation, denoise, deinterlace | Original scripts | Build-specific filters |
| Voice cleanup, music ducking, loudness | Original scripts and audio skills | FFmpeg; listening review |
| Subtitles, karaoke, word captions | Caption tools and skills | Supplied text, or an optional speech engine |
| Bengali/Hindi caption review and retiming | Indic skill and retime-srt | A font covering the script; spelling review |
| Reference analysis and shot evidence | Bundled analysis scripts | Optional uv, image and OCR dependencies |
| Storyboard, product film, wedding and ad planning | Director and storyboard skills | Real source facts and footage |
| B-roll search and rights records | Adapted B-roll skill | Search access and media permission |
| HTML animation and motion components | HyperFrames skills and references | Separate HyperFrames/Node/browser setup |
| React motion graphics and alpha overlays | Bundled MIT motion starter | Remotion dependencies and its own licence |
| Local transcription and word timestamps | cdvea/ai.py transcribe | faster-whisper and an existing local model |
| Content-based scene detection | cdvea/ai.py scenes | PySceneDetect and OpenCV |
| GIF, sticker, hook plates and social variants | Short-form skills and helpers | Some helpers need Node and sharp |
| ProRes, DNxHR, alpha, proxies and platform files | Core export/proxy tools | Appropriate FFmpeg encoders |
| Technical checks, contact sheets and reports | Core tools and render-QC | Some image helpers need extra dependencies |
| Editable video cut handover | export-edl and source-map CSV | Integer 24/25/30 fps; target-editor relink check |
| YouTube upload workflow | Bundled publisher skill | Explicit request, OAuth and account setup |

## Separate software and models

CDVEA includes guidance for AI upscaling, video segmentation and Blender work. It does not bundle their engines, GPU runtimes or model weights. It does not provide native Premiere, Resolve or Final Cut project automation, automatic motion tracking, generative fill, voice cloning or every commercial editor feature.

Use the relevant original project if the job needs [Real-ESRGAN restoration](https://github.com/xinntao/Real-ESRGAN), [SAM 2 segmentation](https://github.com/facebookresearch/sam2) or [Blender](https://www.blender.org/). Review the chosen code and model terms separately. A short sample must show that the tool handles the actual footage before a long run.

The installed environment passed the local core checks. Faster-whisper, PySceneDetect, HyperFrames, Remotion, hosted generation, YouTube upload and native editor imports have not passed an end-to-end test here. VALIDATION.md records the checks that actually ran.
