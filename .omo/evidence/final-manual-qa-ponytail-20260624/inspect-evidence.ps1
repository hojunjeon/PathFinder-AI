$ErrorActionPreference = 'Stop'
$root = (Resolve-Path '.').Path
$outDir = Join-Path $root '.omo\evidence\final-manual-qa-ponytail-20260624'
$files = @(
  '.omo\ulw-loop\ponytail-refactor-20260624\evidence\C001-ponytail-install.txt',
  '.omo\ulw-loop\ponytail-refactor-20260624\evidence\C002-llm-main-pytest.txt',
  '.omo\ulw-loop\ponytail-refactor-20260624\evidence\C003-diff-review.txt',
  '.omo\evidence\ponytail-refactor-direct-verification-20260624.txt',
  '.omo\ulw-loop\ponytail-refactor-20260624\notepad.md'
)
$requiredPatterns = [ordered]@{
  'changed_file_list' = '(?i)(changed file|git diff --name-only|git status|files changed|touched source|modified:)'
  'py_compile' = '(?i)(py_compile|compileall)'
  'llm_28_passed' = '(?i)(28 passed)'
  'backend_84_passed' = '(?i)(84 passed)'
  'frontend_16_passed' = '(?i)(16 passed)'
  'size_receipts_250' = '(?i)(<=\s*250|under\s+250|250\s*LOC|250\s*lines|250-line|size receipt|source modules)'
  'cleanup_receipts' = '(?i)(cleanup|cleaned|no leftover|removed|tear.*down|port|process)'
  'manual_qa_matrix' = '(?i)(manualQa|surfaceEvidence|adversarialCases|artifactRefs)'
  'dirty_ack' = '(?i)(unrelated dirty|dirty files|git status|working tree|worktree)'
}
$result = [ordered]@{}
$result.generatedAt = (Get-Date).ToString('o')
$result.root = $root
$result.files = @()
foreach ($rel in $files) {
  $path = Join-Path $root $rel
  $item = Get-Item -LiteralPath $path -ErrorAction SilentlyContinue
  if ($null -eq $item) {
    $result.files += [ordered]@{ path=$rel; exists=$false; length=0; lastWriteTime=$null; sha256=$null; patternHits=@{} }
    continue
  }
  $content = Get-Content -Raw -LiteralPath $item.FullName
  $hits = [ordered]@{}
  foreach ($key in $requiredPatterns.Keys) {
    $hits[$key] = [bool]([regex]::IsMatch($content, $requiredPatterns[$key]))
  }
  $result.files += [ordered]@{
    path=$rel
    exists=$true
    length=$item.Length
    lastWriteTime=$item.LastWriteTime.ToString('o')
    sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $item.FullName).Hash
    patternHits=$hits
  }
}
$result.gitStatusShort = (& git status --short)
$result.gitBranch = (& git status --short --branch)
$result.gitDiffNameOnly = (& git diff --name-only)
$result.gitDiffCachedNameOnly = (& git diff --cached --name-only)
$result | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $outDir 'S001-evidence-audit.json')
$result | ConvertTo-Json -Depth 8
