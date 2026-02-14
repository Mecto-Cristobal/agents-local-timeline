param(
  [string]$Status = "OK",
  [string]$Text = "Codex progress update",
  [string]$Summary = "",
  [string]$Tags = "system,progress,codex"
)

$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)

$port = if ($env:AGENTS_PORT) { $env:AGENTS_PORT } else { "20000" }
$queue = if ($env:AGENTS_QUEUE_FILE) { $env:AGENTS_QUEUE_FILE } else { "data/wsl_post_queue.ndjson" }
$base = if ($env:AGENTS_BASE_URL) { $env:AGENTS_BASE_URL } else { "http://127.0.0.1:$port" }

$payload = @{
  status = $Status
  job_name = "codex-run"
  human_text = $Text
  result_summary = $Summary
  tags_csv = $Tags
}

$json = $payload | ConvertTo-Json -Compress
try {
  Invoke-RestMethod -Method Post -Uri "$base/api/agents/system/progress" -ContentType "application/json; charset=utf-8" -Body $json | Out-Null
  Write-Output "posted_to=$base"
} catch {
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $queue) | Out-Null
  Add-Content -Path $queue -Value $json -Encoding utf8
  Write-Output "queued_to=$queue"
  Write-Output "reason=no reachable AGENTS endpoint on port $port"
}
