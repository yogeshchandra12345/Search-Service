from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient.http import MediaFileUpload,MediaIoBaseDownload
import io
from tika import parser
from conf import BaseConf
import requests
import json




# # Setup the Drive v3 API
SCOPES = 'https://www.googleapis.com/auth/drive.file'
store = file.Storage('./credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
drive_service = build('drive', 'v3', http=creds.authorize(Http()))

class SearchApplication(object):
	"""
	This class provide Basic Search Service for data stored in Google Drive.

	"""

	def __init__(self, index='test_1'):
		self.es_conn = BaseConf.get_es_conn() 
		self.index = index
		self.doc_type = index
		self.es_url = BaseConf.get_es_url(index)
		self.es_mapping = './es_mapping.json'

	def _ingest_mapping_into_es(self):
		"""
		Ingest Fields mappings into ES index ' test_1'
		Exact term Search is used for all keywords except 'file_info'.
		Text based Search is used for field 'file_info'.
		"""
		if not self.es_conn.indices.exists(self.index):
			with open(self.es_mapping, 'rb') as read:
				data = json.load(read)
				self.es_conn.indices.create(index=self.index, body=json.dumps(data))
				print('Successfully Created mapping for index {}'.format(self.index))
		else:
			print('Index mapping already exists')

	@staticmethod
	def download_file(file_id,filepath):
		"""
		Utility function to download the file from Drive server to local machine.
		:param file_id: A unique file ID for each file present in Google Drive
		:paran filepath: Path to save the file in local machine
		"""
		request = drive_service.files().get_media(fileId=file_id)
		fh = io.BytesIO()
		downloader = MediaIoBaseDownload(fh, request)
		done = False
		while done is False:
			status, done = downloader.next_chunk()
			print("Download {}%%".format(int(status.progress() * 100)))

		with io.open(filepath,'wb') as f:
			fh.seek(0)
			f.write(fh.read())

	@staticmethod
	def upload_file(filename,filepath,mimetype):
		"""
		Utility function to upload the file into Google Drive.
		:param filename: name of the file to upload.
		:param filepath: relative path of file to upload.
		:param mimetype: mimetype of the file to upload.
		"""
		file_metadata = {'name': filename}
		media = MediaFileUpload(filepath,
								mimetype=mimetype)
		file = drive_service.files().create(body=file_metadata,
		                                    media_body=media,
	                                        fields='id').execute()
		print('File ID: {}'.format(file.get('id')))

	
	def _process_and_ingest_to_es(self):
		"""
		Download each file docx file from google drive.
		Extract data points from each file using Tika library parser.
		Ingest the fileID and data ponts of file into ES with id = file_id -> To remove the duplicate records during reingestion of same records.
		"""
		results = drive_service.files().list(pageSize=100,fields="nextPageToken, files(id, name)").execute()
		items = results.get('files', [])

		if items:
			for item in items:
				if item['name'].endswith('.docx'): # Read PDF file from drive
					request = drive_service.files().get_media(fileId=item['id'])
					fh = io.BytesIO()
					downloader = MediaIoBaseDownload(fh, request)
					done = False
					
					while done is False:
						status, done = downloader.next_chunk()
						print("Download {}".format(int(status.progress() * 100)))
				
					# Save pdf file to local
					docx_file_path = './resources/{}'.format(item['name'])
					with io.open(docx_file_path,'wb') as f:
						fh.seek(0)
						f.write(fh.read())
						print('{0} ({1})'.format(item['name'], item['id']))

					# Parse and ingest data into ES
					raw = parser.from_file(docx_file_path)
					text = raw['content'].strip().split('\n')
					row_json = {}
					for _data in text[:6]:
						record = _data.split('=')
						row_json[record[0].strip()] = record[1].strip()
					
					# Append File id to keep track files
					row_json['file_id'] = item['id']
					row_json['file_name'] = item['name']
					self.es_conn.index(index=self.index, body = row_json, id=row_json.get('file_id'))


		
	def find_from_es(self, field):
		"""
		Search By PAN, Name, Contact, Account, File Name etc.
		:param field: Perform the Exact search on Keyword data type and text search on text datatype i.e file_info.
		:return: return the file_id, file_name as a search result of query. Print all the matched records.
		"""

		query = dict(_source=[
	        "Name", "Account_no", "PAN", "Contact", "Email", "file_id", "file_name", "file_info"
	    ], query={
	         "match":{
	      		"file_info": field
	       }
	    })
		headers = {
			"Content-Type": "application/json"
		}
		req = requests.post(self.es_url, data=json.dumps(query), headers=headers)
		file_id_traced = []
		file_name = []
		if req.status_code == 200:
			req_data = req.json()
			req_data = req_data['hits']['hits']
			if req_data:
				for hit in req_data:
					if '_source' in hit.keys():
						hit = hit['_source']
						if hit:
							file_id_traced.append(hit.get('file_id'))
							file_name.append(hit.get('file_name'))
							print(hit)
			else:
				print('No file found with this {}'.format(field))
		return file_id_traced,file_name


myapp = SearchApplication()

#Upload the file to google drive 
# myapp.upload_file('yogesh.docx', './resources/yogesh.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') 
# myapp.upload_file('dummy.docx', './resources/dummy.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')    

myapp._ingest_mapping_into_es()
myapp._process_and_ingest_to_es()

# Search all the files which contains 'income tax' in their file _info.
file_id,file_name = myapp.find_from_es('income tax')
print(file_id, file_name)

if file_id[0]:
	# Download the first search result.
	myapp.download_file(file_id = file_id[0], filepath = './my_searched_file.docx')



