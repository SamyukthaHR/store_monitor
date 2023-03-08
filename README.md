# store_monitor

All restaurants are supposed to be online during their business hours. Due to some unknown reasons, a store might go inactive for a few hours. Restaurant owners want to get a report of the how often this happened in the past.

## APIs
output report schema:
store_id, uptime_last_hour(in minutes), uptime_last_day(in hours), update_last_week(in hours), downtime_last_hour(in minutes), downtime_last_day(in hours), downtime_last_week(in hours) 


1. /trigger_report endpoint that will trigger report generation from the data provided (stored in DB)
        1. No input 
        2. Output - report_id (random string) 
        3. report_id will be used for polling the status of report completion
        
        
2. /get_report endpoint that will return the status of the report or the csv
        1. Input - report_id
        2. Output
            - if report generation is not complete, return “Running” as the output
            - if report generation is complete, return “Complete” along with the CSV file with the schema described above.
            
Installation

To install the required packages, run the following command in the project directory:

    pip install -r requirements.txt
    
Usage

To start the server, run the below command:

    python mange.py runserver
  
  The local server starts running on http://127.0.0.1:8000
  (Example url: http://127.0.0.1:8000/monitor/{end_point})
