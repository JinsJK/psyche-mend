install:
	pip install -r requirements.txt
	@echo Installing system dependency: espeak-ng...
	winget install eSpeak-NG.eSpeak-NG --accept-package-agreements --accept-source-agreements

dev:
	@powershell -Command "Start-Process powershell -ArgumentList '-NoExit', 'cd \"$(CURDIR)\"; .\\psyche-mend-env\\Scripts\\Activate.ps1; uvicorn main:app --reload'"
	@powershell -Command "Start-Process powershell -ArgumentList '-NoExit', 'cd \"$(CURDIR)\\frontend\"; npm run dev'"
	@echo Backend and frontend started in separate terminals.

stop:
	@echo Stopping backend (port 8000) and frontend (port 5173)...
	@powershell -Command "$$p = (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue).OwningProcess; if ($$p) { Stop-Process -Id $$p -Force; Write-Host 'Backend stopped.' } else { Write-Host 'Backend already stopped.' }"
	@powershell -Command "$$p = (Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue).OwningProcess; if ($$p) { Stop-Process -Id $$p -Force; Write-Host 'Frontend stopped.' } else { Write-Host 'Frontend already stopped.' }"
