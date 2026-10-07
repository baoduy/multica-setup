# Multica setup - Improvement loop

A generic presentation animation based on `.archify/workflow-setup-improvement-loop/setup-improvement-loop.html`. Original Archify swimlanes, node positions, and connector routes are preserved. Workspace names, repository owner, endpoint host, agent model, and fixed weekly execution time have been replaced with generic labels. The source diagram is unchanged.

- `improvement-loop-animation.gif`: 1440 × 810, four-second continuous loop at 50 fps. Dots on every arrow travel together, with eased motion, antialiasing, and a gentle fade at the loop boundary.
- `improvement-loop-animation.mp4`: 1920 × 1080, 50 seconds, for narrated presentations.
- `improvement-loop-overview.png`: static overview.
- `improvement-loop-layout.svg`: standalone vector diagram.
- `render_animation.py`: self-contained renderer requiring Pillow, imageio-ffmpeg, and resvg-py. Use `--gif-only` to regenerate only the synchronized GIF.

The GIF shows all connectors moving simultaneously. The narrated video covers monitoring, retrospective, issue creation, scoped fixes, pull request review, release, verified live sync, and both recovery paths in sequence. It illustrates the workflow proposed in the source diagram.
