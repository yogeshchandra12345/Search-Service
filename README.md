### Search based service using Google Drive and ElasticSearch
A basic search service for data stored in online storage services like Google Drive, DropBox or Gmail.

Steps to use this search service on google drive.
* Use a Python API ( oauth2client) to connect to Google Drive.
* Upload two docx file containing having raw text like ('PAN', 'Account No', 'Name', 'File_info', etc).
* Read these files from google Drive and ingest the extracted data into ElasticSearch.
  Ingest each file as a record of data fields like ('Name', 'Account_no', 'PAN', 'Contact', 'Email', File_id', 'File_name',
  'File_info', etc).
* Search based on Exact keyword or string like ('income tax', 'pan', 'file_ingo') in ElasticSearch.


