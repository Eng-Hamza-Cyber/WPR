# WPR - WordPress Reaper v1.0
WPR (WordPress Reaper) is a high-speed, asynchronous security tool designed to harvest sensitive exported files and backups from WordPress upload directories through automated path guessing.

By leveraging the chronological directory structure of WordPress (/year/month/), WPR systematically probes for leaked databases, user exports, and configuration backups that are often left exposed by plugins or site administrators.

# Key Features
Asynchronous Engine: Built with asyncio and httpx for massive concurrency and high performance.

Chronological Fuzzing: Automatically generates paths from the year 2000 to the current date.

Multi-Variant Month Logic: Scans all month formats including numeric (01), full name (January), and short name (Jan).

Advanced Detection:

Directory Listing: Detects "Index of" pages to expose entire folder contents.

Soft 404 Protection: Uses Content-Type validation to filter out fake 200 OK responses.

Stealth Mode: Rotates through a pool of 20 unique User-Agents to bypass basic WAF patterns.

HTTP/2 Support: Utilizes modern protocol features for improved connection stability.


# Installation

## 1.Clone the Repository:

`git clone https://github.com/Eng-Hamza-Cyber/WPR.git`

## 2.Install Dependencies:
`pip install -r requirements.txt`

## 3.Prepare Wordlist:
Ensure your db.txt file is in the root directory with the filenames you wish to target (e.g., export-users.csv, backup.sql).

# Usage

## Run the tool using the following command-line arguments:
`#Standard scan with default settings
python wpr.py -t https://example.com

#Start scanning from a specific year
python wpr.py -t https://example.com -s 2018

#Increase concurrency for faster results
python wpr.py -t https://example.com -c 20`

## Argument Reference
Flag,Description,Default
"-t, --target",Target WordPress URL (Required),None
"-s, --start",The year to begin scanning from,2000
"-c, --concurrency",Number of simultaneous requests,5

# Output
Any successfully discovered files or exposed directories are immediately logged to results.txt in the following format:

`[+] FOUND: https://example.com/wp-content/uploads/2024/01/users.csv`

`[DIR] https://example.com/wp-content/uploads/2023/12/`

# Disclaimer
This tool is for educational purposes and authorized security auditing only. The developer assumes no liability for misuse or damage caused by this tool. Only use WPR on systems you have explicit permission to test.
