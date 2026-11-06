Write-Host "=== [1/2] RUNNING AUTOMATED UNIT TESTS (CORE, GUI & PSD FONTS AC-01 -> AC-22) ===" -ForegroundColor Cyan
& "C:\JerseyShift\.venv\Scripts\python.exe" -m unittest discover -s "C:\FRAYED_TEXT_PNG_GENERATOR\tests" -p "test_*.py" -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Tests failed!" -ForegroundColor Red
    exit 1
}

Write-Host "=== [2/2] RUNNING CLI ACCEPTANCE RENDER ===" -ForegroundColor Cyan
& "C:\JerseyShift\.venv\Scripts\python.exe" "C:\FRAYED_TEXT_PNG_GENERATOR\run_cli.py" --text "Hoffenheim" --color "#074BAC" --output "C:\FRAYED_TEXT_PNG_GENERATOR\output\Hoffenheim_acceptance.png"
if ($LASTEXITCODE -eq 0) {
    Write-Host "[PASS] All Acceptance Criteria (Core + GUI) PASS 100%!" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Acceptance render failed!" -ForegroundColor Red
    exit 1
}
