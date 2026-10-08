# Multica setup - git flow

The approved version retains the original Archify swimlanes, node positions, colors, and connector routes, with animated highlights and captions. The original diagram source is unchanged.

- gitflow-archify-animation.gif: 1440 × 810, four-second continuous loop at 50 fps. Dots on every arrow travel together, with eased motion, antialiasing, and a gentle fade at the loop boundary.
- gitflow-archify-animation.mp4: 1920 × 1080, 50 seconds, H.264; retains the slower pace for presenting with narration.
- gitflow-archify-overview.png: 1920 × 1080 static overview.
- gitflow-archify-layout.svg: standalone vector diagram with original geometry.
- render_archify_animation.py: self-contained renderer; requires Pillow, imageio-ffmpeg, and resvg-py. Regenerates the synchronized GIF and narrated video; use `--gif-only` to update only the GIF.

The GIF shows all connectors moving simultaneously. The narrated video covers all seven main-path nodes, owner rejection, blocked sync, and manual --accept recovery in sequence. This depicts the proposed workflow.

The earlier simplified version and temporary preview images have been removed.
