PathFiner AI slide image generation run

Requested skills:
- ulw-loop: user explicitly invoked it; using LIGHT workflow because this is an image/deck artifact delivery with no code edits, schema, auth, DB, or external runtime integration.
- imagegen: user explicitly requested generated image slides and forbade Python script/SVG generation.

CLI/model availability:
- `omo ulw-loop help` check returned `ULW_MISSING`, so durable state is recorded here instead of through the unavailable CLI.
- `OPENAI_API_KEY` check returned `OPENAI_API_KEY_MISSING`, so the explicit `gpt-image-2` CLI path is unavailable without asking for credentials.
- User allowed fallback to an image generation model; use built-in `image_gen`.

Success criteria:
- C1: Produce six 16:9 Korean presentation slide images for a 5-7 minute two-person project presentation.
- C2: Follow `PT/DESIGN.md`: aubergine primary, cream/lavender/pastel mesh, floating UI/product mockups, restrained text, diagram/table/flow visual emphasis.
- C3: Include compact presenter-note keywords on every slide.
- C4: Incorporate competitor differentiation based on current web research: Saramin AI mock interview, Teal AI Interview Agent, Kickresume Interview Questions Generator, Google Interview Warmup.

Manual QA surface:
- Auxiliary surface: generated image files saved under `PT/generated_slides/`.
- Evidence: final file listing plus visual inspection of each generated slide.

Evidence captured:
- `PT/generated_slides/slide-01.png` through `slide-06.png` copied from built-in image generation output.
- `file PT/generated_slides/slide-*.png` reported every slide as PNG image data, `1672 x 941`, RGB, non-interlaced.
- Visual inspection opened all six slides and confirmed: aubergine/pastel design, sparse Korean slide text, diagram/table/graph visuals, and presenter-note footer pills.
- Cleanup: no server, tmux session, browser context, bound port, temp dir, or container was spawned for QA.
