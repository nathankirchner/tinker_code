# GWA Proposal Maker

This Python script generates professional proposals for Grey Wall Advisory client engagements.

## Prerequisites

- Python 3.7 or higher
- OpenAI API key

## Required Files

The following files must be present in the same directory as the script:

- `COMPANY.txt` - Contains the client company name
- `GOAL.txt` - Contains the engagement goals
- `SOW.txt` - Contains the Statement of Work
- `COSTS-TIMELINES.txt` - Contains costs and timeline information
- `GWA_logo.png` - Grey Wall Advisory logo
- `nk_QR_footer.png` - QR code footer image

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

## Usage

1. Ensure all required text files and images are in the same directory as the script
2. Run the script:
   ```bash
   python GWA_proposal_maker.py
   ```

If any required files are missing, the script will prompt you to select a directory containing the files.

The generated PDF will be saved in the same directory as the script, named `GWA_Proposal_[COMPANY_NAME].pdf`. 