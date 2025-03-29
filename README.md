# About

The script for Kazakhstan's Kaspi Bank PDF transactions statement parsing. It converts PDF with transactions to a CSV format, which is supported by [YNAB](https://www.ynab.com/) budget web-app for import.

# Installation as a "Send To" script for Windows

1. Install Python from a Microsoft Store
2. Add a "Send To" script:
  * Press `Win+R`
  * Run `shell:sendto`
  * Move a Windows Shortcut file from a repository folder
  * Open Shortcut properties and adjust path to `C:\[Path To Project]\KaspiParser\run_kaspi_parser.bat`

After installation the script becomes visible in the Windows context menu. After execution the result CSV file will be placed next to input PDF transaction file.

![image](https://github.com/user-attachments/assets/bdb54bab-b8f1-4b2d-b327-a740b1037a76)
