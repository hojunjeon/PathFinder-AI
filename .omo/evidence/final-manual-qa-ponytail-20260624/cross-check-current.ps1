$ErrorActionPreference = 'Stop'
$root = (Resolve-Path '.').Path
$outDir = Join-Path $root '.omo\evidence\final-manual-qa-ponytail-20260624'
$sourceFiles = @(
  'llm_server/main.py',
  'llm_server/roadmap_prompt.py',
  'llm_server/roadmap_processing_competency.py',
  'llm_server/roadmap_processing_timeline.py',
  'llm_server/roadmap_processing_values.py',
  'llm_server/tests/test_roadmap_prompt.py',
  'llm_server/tests/test_roadmap_processing_values.py',
  'frontend/src/views/AnalyzeResultView.vue',
  'frontend/src/components/result/InterviewDrill.vue',
  'frontend/src/components/result/PreparationKeywordBoard.vue',
  'frontend/tests/e2e/analyze-flow.spec.js',
  'frontend/scripts/verify-design.mjs'
)
$counts = @()
foreach ($rel in $sourceFiles) {
  $path = Join-Path $root $rel
  if (Test-Path -LiteralPath $path) {
    $lines = (Get-Content -LiteralPath $path | Measure-Object -Line).Lines
    $counts += [ordered]@{ path=$rel; exists=$true; lines=$lines; le250=($lines -le 250) }
  } else {
    $counts += [ordered]@{ path=$rel; exists=$false; lines=$null; le250=$false }
  }
}
$status = (& git status --short)
$dirtySource = $status | Where-Object { $_ -match '(^..\s+(frontend|llm_server|backend)/|^\?\?\s+(frontend|llm_server|backend)/)' }
$evidenceText = Get-Content -Raw -LiteralPath (Join-Path $root '.omo\ulw-loop\ponytail-refactor-20260624\evidence\C003-diff-review.txt')
$result = [ordered]@{
  generatedAt=(Get-Date).ToString('o')
  sourceLineCounts=$counts
  dirtySourceFiles=$dirtySource
  evidenceC003Mentions = [ordered]@{}
}
foreach ($rel in $sourceFiles) {
  $result.evidenceC003Mentions[$rel] = $evidenceText.Contains($rel)
}
$result | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $outDir 'S002-current-cross-check.json')
$result | ConvertTo-Json -Depth 8
