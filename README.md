# nexove

Static site export (Nuxt). Local preview:

```bash
./scripts/dev.sh
```

Opens [http://localhost:3000](http://localhost:3000). Before serving, `dev.sh` runs `sync-newstar.sh`.

## Sun / `newStar` texture

The rotating background Sun uses a **PNG** texture (`textures/newStar.png`), not SVG.

1. Edit the source file: `images/svg/newStar.svg`
2. For the **full logo** (all thorns/spikes), keep `images/newStar-master.png` updated — white logo on **black** background (export from Figma/Photoshop). `sync-newstar.sh` uses this file when present.
3. Sync to PNG (automatic when using `./scripts/dev.sh`):

```bash
./scripts/sync-newstar.sh
```

Optional size (default 1024):

```bash
NEWSTAR_SIZE=2048 ./scripts/sync-newstar.sh
```

`sync-newstar.sh` also strips macOS Quick Look’s white matte so the WebGL Sun shows your logo shape, not a solid square.

Commit both `images/svg/newStar.svg` and `textures/newStar.png` when deploying so GitHub Pages has the latest logo. After syncing, hard refresh the browser (`Cmd+Shift+R`).
