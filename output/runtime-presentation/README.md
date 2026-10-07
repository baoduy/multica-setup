# Multica setup - Runtime architecture

Animation of `.archify/architecture-runtime/runtime.html`, preserving its node positions, labels, colors, and connector routes.

- `runtime-animation.gif`: 1440 × 1440, four-second continuous loop at 50 fps. Small dots on all 11 arrows travel simultaneously, with eased motion, antialiasing, and a gentle fade at the loop boundary.
- `runtime-overview.png`: static overview.
- `runtime-layout.svg`: standalone vector diagram.
- `render_animation.py`: renderer requiring Pillow and resvg-py. Run it to regenerate the artifacts.

The square canvas accommodates the source diagram's tall layout and shows the complete architecture.
