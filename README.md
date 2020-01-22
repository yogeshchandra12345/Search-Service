#### Search based service using Google Drive and ElasticSearch
A basic search service for data stored in online storage services like Google Drive, DropBox or Gmail.
##### Steps to use this search service on google drive.
* Use a Python API ( oauth2client) to connect to Google Drive.
* Upload two docx file containing having raw text like ('PAN', 'Account No', 'Name', 'File_info', etc).
* Read these files from google Drive and ingest the extracted data into ElasticSearch.
  Ingest each file as a record of data fields like ('Name', 'Account_no', 'PAN', 'Contact', 'Email', File_id', 'File_name',
  'File_info', etc).
* Search based on Exact keyword or string like ('income tax', 'pan', 'file_ingo') in ElasticSearch.


##### Code File Structure:
* Python version : `3.6.8`
1. `client_secret.json/credential.json` ( Token,refresh_token and secret_id to access Drive API)
2. `resources` named folder contains two docs file ( yogesh.docx and dummy.docx)
3. `main.py` is entry point of our application.
4. `conf.py` contains configurations related to ElasticSearch.
5. `es_mapping.json` contains mapping of each field to Keyword, text according to the search requirement.
6. `requirements.txt` contains project dependencies.

##### Examples:
* Content of first file `yogesh.docx`:
```
Name = Yogesh
Account_no = 5555544444
PAN = ABCDE1234F
Contact = 9773990308
Email = yogesh.chandra.eee13@itbhu.ac.in 
file_info = bank statement file
```
* Content of second file `dummy.docx`:
```
Name = Test_User
Account_no = 6666677777
PAN = QWERT1234Y 
Contact = 9421408696
Email = test_user@gmail.com
file_info = income tax file
```
