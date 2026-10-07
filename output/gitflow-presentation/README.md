# Git flow presentation animation

Based on `.archify/workflow-setup-gitflow/candidate.json`. This is a presentation of the **proposed** workflow, not a claim that it has been deployed.

- `gitflow-presentation.mp4`: 1920 × 1080, 42 seconds, H.264 video. Recommended for presentation slides. Set playback to automatic and enable looping if desired.
- `gitflow-presentation.gif`: 1280 × 720, 42-second continuous loop. Insert as an image into a presentation and view it in slideshow mode.
- `gitflow-overview.png`: 1920 × 1080 static overview, useful as a handout or fallback slide.
- `render_animation.py`: editable source for regenerating the outputs with Pillow and imageio-ffmpeg.

The animation walks through six stages, then illustrates rejection and blocked-sync recovery. The source's dev-tip push is combined with the fix step to keep the presentation readable. Owner-only merge, one reused PR, verification before moving the tag, and an unchanged tag on failure are retained.

Additional implementation rules in the source: changes are scoped to the drunk bundle; the steward uses the agent/setup-steward worktree, pushes HEAD:refs/heads/dev, and verifies with git ls-remote; no feature branch or bare git push is used; dev is never force-pushed; only live/drunk is force-moved after verification. Unsupported sync exits with code 2 and requires manual steps before rerun --accept.

Animation timing: overview 3 seconds; six primary stages 4 seconds each; rejection recovery 5 seconds; blocked-sync recovery 5 seconds; summary 5 seconds. No audio.
