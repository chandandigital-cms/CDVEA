# Make a cut assembly

Run commands from the plugin root. The Python CLI uses only the standard library. Media rendering needs FFmpeg with libx264 and AAC, plus FFprobe.

```powershell
python cdvea/cli.py init "D:/VideoJobs/venue-promo"
python cdvea/cli.py validate-plan "D:/VideoJobs/venue-promo/edit-plan.json"
python cdvea/cli.py render-plan "D:/VideoJobs/venue-promo/edit-plan.json" --dry-run
python cdvea/cli.py render-plan "D:/VideoJobs/venue-promo/edit-plan.json"
```

Fill the project file before validation. Use real local media paths and seconds. Relative paths resolve from the plan’s directory. This example describes a 5-second assembly; it is a schema example, not a promise that those source files exist.

```json
{
  "version": 1,
  "name": "Venue promo",
  "width": 1080,
  "height": 1920,
  "fps": 30,
  "clips": [
    {"source": "media/entrance.mp4", "start": 2, "end": 5, "label": "Entrance"},
    {"source": "media/hall.mp4", "start": 0, "end": 4, "speed": 2}
  ],
  "output": "outputs/promo-v1.mp4"
}
```

The helper supports hard cuts, source ranges and speed from 0.25 to 4. It pads the picture without cropping, converts to the chosen constant frame rate and writes SDR H.264/AAC MP4. Missing audio becomes silence. It rounds each clip’s output length to the nearest frame. It refuses HDR/wide-gamut inputs, unknown fields, source overwrites and existing output files. Convert colour deliberately with the core colour tool first. Audio fades cover 15 ms at each clip edge, or less for a short clip.

Dry-run probes the sources and returns timing without writing render artifacts. Rendering creates temporary clips beside the output, checks geometry and duration, fully decodes the candidate and then copies it to a new file. An interrupted copy can leave a partial final file; choose a fresh filename after inspecting it. The helper does not judge picture quality, lip sync or story flow.

Use the workbench for overlapping tracks, transitions, masks, titles or arbitrary filter graphs. Use core export.py for delivery codecs and loudness.py for a measured mix. The assembly helper does not preserve camera metadata, surround layout, alpha or embedded source timecode.

## Retime a source subtitle file

```powershell
python cdvea/cli.py retime-srt edit-plan.json --source media/entrance.mp4 --srt entrance.srt --output entrance-retimed.srt
```

Use one source subtitle file per call. Repeated clips produce repeated cues. Cuts split or trim crossing cues; speed changes alter timing. The helper does not know word boundaries. Listen to every split before burning captions. Merge captions from several sources with an overlap check.

## Move video cuts to another editor

```powershell
python cdvea/cli.py export-edl edit-plan.json --output review/cuts.edl
```

This creates a CMX 3600 video cut list and a source-map CSV. It supports integer 24, 25 and 30 fps without speed changes. It uses zero-based media time and synthetic reel IDs. Audio, transitions, effects, titles and embedded source timecode do not transfer. Relink and check it in the target editor; no native editor import test has run for this release.
