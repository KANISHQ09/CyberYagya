📱 Mobile Forensic Triage Tool

🔍 Overview

The Mobile Forensic Triage Tool is a GUI-based application designed to extract, preview, and export critical data from Android devices without rooting. It enables investigators and analysts to perform initial triage of mobile devices in a secure and efficient manner.

This tool is particularly useful for cybercrime investigations, incident response, and digital evidence collection in field environments.

🎯 Key Features

🔌 ADB-based Device Connection – No root required

📞 Call Logs – View and export call history

💬 SMS Messages – Filter and extract text messages

🖼️ Media Files – Preview and save images/videos

🕒 Timestamp Filters – Search data within specific time ranges

📤 Export Options – Save extracted data as PDF or CSV

🧑‍💻 User-Friendly GUI – Built with Tkinter for non-technical users

🔐 Forensic-Safe – Read-only operations to maintain data integrity

🧰 Tech Stack

Python

ADB (Android Debug Bridge)

Tkinter – for GUI

SQLite3 / pandas – for data parsing and filtering


🧪 How It Works

Connect Android device via USB with USB debugging enabled

Tool uses ADB to pull selected files 

Extracted data is parsed and previewed in the GUI

User can filter data and export to PDF/CSV

💡 Use Cases

Rapid triage in cybercrime units

On-field mobile device screening

Educational tool for digital forensics learners

Legal evidence collection with minimal footprint
