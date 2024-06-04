# MyChartWebScraper 

This is a basic program that extracts medication and dosing information from the my chart website. 
Hopfully others can use this as a starting point for taking charge of their (or their loved ones) treatment data.

## Description

The MyChart UI can be limiting in terms of
* the short history of treatment notes available
* The lack of analytics tools (particularly day to day change tracking)
* The mutablility of historical data

This web scraper aims to solve these porblems by pulling data from the MyChart website and logging results in an append only datastore (google sheets).

## Getting Started


### Dependencies

- Log in information for the patient for whom data is needed
- A google sheet file and corresponding sheetId
- A GCP API key with permissions to update and read data fom said google sheet
     - Credentials to be stored in 'credentials.json' in the project's root directory

### Installing

* TBA

### Executing program

* TBA

## Authors

Collin Wischmeyer (cjwischmeyer@gmail.com)

## Version History

* 0.1
    * Functionality to read and write from google sheet
    * Ability to process data from the 'Daily Meds' day at a glance page
        * www.*...*.org/MyChart-prd/inside.asp?mode=itinerary
    * Ability to segment out unique medications
