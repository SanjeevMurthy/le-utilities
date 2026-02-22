# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

**le-utilities** is a personal collection of standalone utility scripts and educational materials. Each subdirectory is an independent tool with its own dependencies and execution method. There is no unified build system.

## Running Components

Each component is a standalone Python script or shell script:

**Python scripts**: Navigate to directory, install dependencies, run with `python script_name.py`
**Shell scripts**: Run with `bash script_name.sh` or make executable first

### Component-Specific Instructions

| Component                       | Run Command                                                       | Dependencies                   |
| ------------------------------- | ----------------------------------------------------------------- | ------------------------------ |
| anki/                           | `python consolidate_commands.py`, `python generate_cka_pdf.py`    | PDF generation libs            |
| excel-tools/                    | `python analyze_instagram_data.py`                                | pandas                         |
| md-to-pdf/                      | `python convert_md.py [source.md] [output.pdf]`                   | markdown, Chrome installed     |
| web-automation/                 | `python login-screenshot.py`                                      | selenium, webdriver-manager    |
| custom-llm/                     | `python chat-phi4.py`                                             | openai                         |
| youtube/download-playlist/      | `python youtube_playlist_noapi.py`                                | yt-dlp                         |
| youtube/download-transcription/ | `python youtube_transcription.py`                                 | youtube-transcript-api, yt-dlp |
| mac/                            | `bash install_p10k.sh`, `bash uninstall_app.sh [app] [--dry-run]` | Homebrew                       |

## Architecture

- **No shared code** - Each directory is completely independent
- **No tests** - No testing framework is configured
- **macOS-focused** - Scripts assume macOS paths and tools
- **Credentials** - Some scripts have hardcoded credentials that should be moved to environment variables

## Component Purposes

- **anki/**: Generate Kubernetes certification (CKA/CKAD) flashcard PDFs from command databases
- **excel-tools/**: Analyze Instagram data from Excel files, detect duplicates, generate statistics
- **md-to-pdf/**: Convert Markdown to styled PDF via headless Chrome
- **web-automation/**: Selenium scripts for website login and screenshot automation
- **custom-llm/**: Azure OpenAI API integration for Phi-4 model queries
- **youtube/download-playlist/**: Extract video URLs from YouTube playlists (no API key needed, uses yt-dlp)
- **youtube/download-transcription/**: Download English transcripts from YouTube — supports single video, full playlist, or batch from a URL text file
- **vi editor tutorial/**, **terminal shortcuts/**: Educational markdown documentation
- **mac/**, **setup-dev/**: Shell scripts for macOS environment setup
