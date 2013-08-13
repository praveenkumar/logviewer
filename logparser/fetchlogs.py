import urllib2
import json
from bs4 import BeautifulSoup
import os
import time

log_directory = "/var/tmp/logviewer"

def  fetch_logs(log_path=None, log_url=None):
	
	"""
	Provide the timeout if you are using a slow network connection
	otherwise it will show the exception 'IOError'.
	"""

	# Initial all the data before using.
	log_dict = {}


	try:
		if not os.path.exists(log_directory):
			os.makedirs(log_directory)
	except:
		print "Not able to create /var/tmp/logviewer directory"

	try:
		json_file = open("%s/log.json" % (log_directory))
		if os.stat("%s/log.json" % (log_directory)).st_size == 0:
			raise IOError
	
	except IOError as err:
		print "Json file not present making from scratch"
	
	else:
		print "Should not go to this block"
		log_dict = json.load(json_file)
		json_file.close()

	# If url set and fetching logs from there.
	if log_url:
		print "Log URL is set"
		log_dict = fetch_url_log(log_dict, log_url)

	if log_path:
		print "Log Path is Set"
		log_dict = fetch_path_log(log_dict, log_path)

	json_file = open("%s/log.json" % (log_directory), 'w')
	json.dump(log_dict, json_file)
	json_file.close()

def fetch_url_log(log_dict, log_location_url):
	try:
		if ".log" in log_location_url:
			log_dict = read_url_log(log_dict, log_location_url)

		else:
			url_object = urllib2.urlopen(log_location_url, timeout=30)
			soup_object = BeautifulSoup(url_object.read())
			url_object.close()
			for link in soup_object.find_all('a'): 
	  			if ".log" in link.get('href'):
	  				log_url = ("%s%s") % (log_location_url, link.get('href'))
	  				log_dict = read_url_log(log_dict, log_url)

	except IOError as err:
		print "Error: ", err

	return log_dict

def read_url_log(log_dict, log_url):

	log_id = log_url.split('/')[-1] 
	print "Now reading %s" % (log_url)
	log_file = urllib2.urlopen(log_url, timeout=30)
	if log_id not in log_dict:
		log_dict[log_id] = {
							  	'date' : log_file.info()['Last-Modified'],
							  	'content' : log_file.read(),
							  	'size' : log_file.info()['Content-Length']
						  	} 
	log_file.close()
	return log_dict

def fetch_path_log(log_dict, log_path):
	
	if ".log" in log_path:
		print "Given Path represent a file"
		read_path_log(log_dict, log_path)
	else:
		print "Given Path reperent a directory"
		for root, dirs, files in os.walk(log_path):
			print files
			if files:
				for log_file in files:
					if ".log" in log_file:
						log_file_path = os.path.join(log_path, log_file)
						read_path_log(log_dict, log_file_path)
	
	return log_dict			

def read_path_log(log_dict, log_file_path):
	log_id = log_file_path.split('/')[-1]
	if log_id not in log_dict:
		log_dict[log_id] = {
							  	'date' : time.ctime(os.stat(log_file_path).st_mtime),
							  	'content' : open(log_file_path).read(),
							  	'size' : os.stat(log_file_path).st_size
						  	}
	
	return log_dict 

if __name__ == '__main__':
	fetch_logs(log_url="http://www.dgplug.org/irclogs/2013/")
