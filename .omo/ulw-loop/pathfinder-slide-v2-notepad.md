PathFiner AI slide v2 orchestration

Tier: HEAVY
Justification: user explicitly requested multi-agent orchestration, live requirement monitoring, evaluation, and repetition until requirements are satisfied.

Skills used:
- ulw-loop: explicitly invoked by user for evidence-led orchestration.
- imagegen: task requires raster image slide generation and forbids Python script/SVG generation.

Non-negotiable requirements:
- Regenerate the slide images; do not just explain.
- No literal text like `발표자 노트:` inside slides.
- Presenter hints must be visually integrated as subtle microcopy, small chips, margin cues, or callout labels.
- Each slide must share a consistent template: same header placement, same content grid, same palette, same bottom-right page-number treatment.
- Page number must be bottom-right, e.g. `01/06`, `02/06`.
- Follow `PT/DESIGN.md` as the active design reference.
- Use generated images, not Python scripts, not SVG.
- Orchestrate separate agents in sequence: research -> image prompt plan -> image generation -> evaluation.
- Maintain a monitoring agent and intervene if work diverges from user requirements.

Success criteria:
- C1: Six 16:9 Korean slide PNGs exist under `PT/generated_slides_v2/slide-01.png` ... `slide-06.png`.
- C2: Every slide has bottom-right page number and no `발표자 노트:` text.
- C3: Slides share a recognizable template: header band, content area, integrated hint chip, page number, consistent color/typography.
- C4: Slide 4 includes competitor differentiation based on current research.
- C5: Evaluation agent approves, or any rejection is addressed by a regeneration pass.

Manual QA / evidence:
- Auxiliary surface: file listings, image dimensions, visual inspection.
- Agent evidence: research, prompt plan, generation report, monitoring notes, evaluation verdict.

Execution evidence:
- Monitoring agent `Pascal`: preflight blockers defined, then returned `READY-FOR-GENERATION`.
- Research agent `Kant`: competitor research completed; slide 4 should frame PathFinder AI as a pre-interview preparation engine, not a mock-interview clone.
- Prompt-planning agent `Peirce`: produced a shared template and six per-slide prompts with no `발표자 노트:` literal, integrated hint chips/callouts, and `01/06`-`06/06` numbering.
- Generation coordination agent `Goodall`: PASS. Confirmed `slide-01.png` through `slide-06.png` present under `PT/generated_slides_v2/`, PNG format, `1672 x 941`, effective 16:9, correct page numbers, no visible `발표자 노트:`, consistent template.
- Evaluation agent `Bacon`: OVERALL PASS. No regeneration requested. Confirmed all slides satisfy visible requirements and slide 4 competitor framing.
- Orchestrator visual inspection: all six images opened; each uses the v2 consistent restrained template, bottom-right page number, and integrated presenter hint chip/callout.
- A final PowerShell dimension re-check using `[System.Drawing.Image]` failed because the type was unavailable in this runtime; this did not block because two agent reviews already recorded dimensions and visual PASS.
- Cleanup: no dev server, browser context, tmux session, container, bound port, or temp runtime remained. Subagents were closed after completion.
