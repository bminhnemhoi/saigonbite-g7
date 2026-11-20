param([string]$In, [string]$Out)
$ppt = New-Object -ComObject PowerPoint.Application
try {
  $p = $ppt.Presentations.Open($In, $true, $false, $false)
  $p.SaveAs($Out, 32)
  $p.Close()
} finally {
  $ppt.Quit()
  [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
}
