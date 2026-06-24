# Codex gpt-5.5 subagent extract

## Current page evaluation

- Input data for analyze/13 is sufficient: company, job, interview type, 14 roadmap categories, and 5 competency items were available.
- The current result page renders the right data, but the information architecture is too expanded. All 14 category cards are visible as a long scroll wall.
- The repeated evidence coverage bars all showing 100% do not help the user decide what to prepare first.
- Answer quality is directionally good: it identifies motion control and embedded IO as strengths, and EtherCAT/TCP/IP plus ROS2/C++/Linux as the main preparation gaps.
- The top of the page should compress the judgment into one practical recommendation before showing detail.

## Proposed ideal page

- First viewport: role, company, technical-interview context, one-line diagnosis, and a practical readiness score.
- Priority block: the three preparation actions the applicant should do today.
- Competency board: strength, explanation gap, and insufficient-data items separated visually.
- Job-duty matrix: compact rows for duty, judgment, and interview talking point instead of 14 expanded cards.
- Expected questions: concise technical questions mapped to the highest-risk duties.

## Artifact

See `codex-ideal.html` in this folder.
