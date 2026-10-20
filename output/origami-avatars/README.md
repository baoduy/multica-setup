# Origami animal avatars

Generated with the built-in `image_gen` tool on 2026-09-16.

19 named PNG files cover 15 agents, three squads, and the workspace. They use 22 shared animal designs. Images are 1254 × 1254 pixels with opaque warm ivory backgrounds.

Open `index.html` locally to browse, filter by workspace or type, preview circular cropping, and download individual files.

- `drunk-workspace/agents/`: 15 agent avatars.
- `drunk-workspace/squads/`: three squad avatars.
- `drunk-workspace/workspace.avatar.png`: workspace avatar.
- `animals/`: 22 original generated designs in the repository. The ZIP omits these duplicate masters and includes all 19 named avatar files instead.
- `generation-plan.json`: exact prompts, complete assignment mapping, dimensions, and SHA-256 checksums.

Existing animal identities follow the original avatar images or configured emoji. The architecture reviewer uses a gold owl, spec reviewer a silver owl, and product owner a chestnut owl. Existing star and moon symbols become a starfish and lunar moth. The workspace design is a navy crane, reflecting drunk's brand colors.

These are locally staged assets. The export bundles and live workspace configuration have not been modified. This folder is an avatar collection, not a Multica import bundle.

To rebuild the gallery after changing the assignment mapping or files:

```sh
python3 output/origami-avatars/build_gallery.py
```
