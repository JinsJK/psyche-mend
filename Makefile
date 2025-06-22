dev:
	@powershell -Command "Start-Process powershell -ArgumentList '-NoExit', 'cd \"$(CURDIR)\"; .\\psyche-mend-env\\Scripts\\Activate.ps1; uvicorn main:app --reload'"
	@powershell -Command "Start-Process powershell -ArgumentList '-NoExit', 'cd \"$(CURDIR)\\frontend\"; npm run dev'"
	@echo Backend and frontend started in separate terminals.

stop:
	@echo Stopping backend (uvicorn) and frontend (node)...
	@taskkill /F /IM python.exe /FI "WINDOWTITLE eq uvicorn*" 2>nul || echo Backend already stopped.
	@taskkill /F /IM node.exe 2>nul || echo Frontend already stopped.
