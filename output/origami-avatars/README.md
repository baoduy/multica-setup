# Origami animal avatars

Generated with the built-in `image_gen` tool on 2026-09-16.

40 named PNG files cover all 32 agents, six squads, and two workspaces. They use 22 shared animal designs. Images are 1254 × 1254 pixels with opaque warm ivory backgrounds.

Open `index.html` locally to browse, filter by workspace or type, preview circular cropping, and download individual files.

- `drunk-workspace/agents/`: 15 agent avatars.
- `mx-workspace/agents/`: 17 agent avatars.
- Each workspace's `squads/`: three squad avatars.
- Each workspace's `workspace.avatar.png`: workspace avatar.
- `animals/`: 22 original generated designs in the repository. The ZIP omits these duplicate masters and includes all 40 named avatar files instead.
- `generation-plan.json`: exact prompts, complete assignment mapping, dimensions, and SHA-256 checksums.

Existing animal identities follow the original avatar images or configured emoji. The architecture reviewer uses a gold owl, spec reviewer a silver owl, and product owner a chestnut owl. Existing star and moon symbols become a starfish and lunar moth. The workspace designs are a navy crane (drunk) and mint manta ray (mx), reflecting their existing brand colors.

These are locally staged assets. The export bundles and live workspace configuration have not been modified. This folder is an avatar collection, not a Multica import bundle.

To rebuild the gallery after changing the assignment mapping or files:

```sh
python3 output/origami-avatars/build_gallery.py
```
