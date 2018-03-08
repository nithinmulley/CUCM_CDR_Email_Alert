CDR Email Alerts
	Sole purpose of this script is to generate an email whenever a call was made to Emergency Number (ex: 911 in US). This is useful in large organisations where there is an internal security and atleast a first level of medical assistance within the premises which can attend to the caller if required way before Emergency Dispatch reaches the premises. (Like a Hospital where I have implemented this). This can also address any accidental dials to Emergency services by identifying the caller and educate them. Lot of times if thats an accidental dial to the Emergency Services, they can stay on call and tell that it was accidental instead of just hanging up the call.

	You can certainly make more changes as per your requirement. This script is a demonstration of CDR records can be parsed 24x7 and send admins alerts on certain calls.

Requirements:
	Python and related Packages:
	Python 3.x
	six(1.11.0) - {pip install six}
	suds-jurko(0.6) - {pip install suds-jurko}

	CUCM AXL Credentials:
	-> Goto CUCM Administration -> User Management -> Application User -> Add New.
	-> Provide the AXL username and password that you'll use in the script. Under the Permissions Information, add to group 'AXL User'.

	WSDL Path:
	-> Goto CUCM Administration -> Application -> Plugins. Download 'Cisco AXL Toolkit'.
	-> Extract and explore to axlsqltoolkit-> Schema-> (the corresponding version of your CUCM) -> AXLAPI.wsdl. Place this on the same system as your script is running. Path to this file goes in the script against 'wsdl' variable. 

	CDR Dump Paths:
	This script will run on the same system which has FTP/SFTP service so that Call manager can store CDR records.
	-> Will require 2 directories. One for the Call manager to push the new files and one to move the files to after the script has processed them.
	-> Lets say, 	CDR_new -> Call manager to store new records.
					CDR_archive -> To store the processed records.
	-> Provide paths to these folders in the script.

	CUCM CDR Store:
	-> Goto https://callmanager/ccmservice/cdrconfiguration.jsp (replace callmanager with your callmanager IP address).
	-> Under Billing Application Server Parameters, Add FTP/SFTP server with the path to 'CDR_new' folder where Call Manager will send all the CDR files to be processed by this script. If you already have a Billing server, Do not touch that.

	file_log_911:
	-> this csv file is used to store all the processed records (matched records) apart from sending email alerts. This serves as a quick reference on the volume and can help as data source for reporting on such calls.
	-> Provide the path to the file in the script.

	Email Parts::
	Relay Server:
	-> provide IP address of the Relay server. Make sure your system IP where this script is running is whitelisted on the Relay server.

	email_from_default:
	-> Provide a 'from' address here to used in your email alerts.

	email_dict:
	-> Provide a default 'to' address against key 'def'. This can be a single address or multiple address. Ex: 'def': ['nit.tin@xyz.xyz', 'meg.han@xyz.xyz']
	-> This dictionary variable defines whom to send the alert for different locations. We have defined naming conventions for GW Names (SIP Trunk Names) or partition names on the call manager as per the location. Say the Gateway name is CP101VG1, I can easily have 'CP101' as a key to identify that particular location and have email addresses concerned to that location as values against it. If you do not want this, just go with 'def' key and have all your email addresses against it.


Usage:
	-> After all the requirements are satisfied and all the inputs have been provided in the Script, you can either run this script manually from CMD to test or schedule the script using Task scheduler on windows for 24x7 processing of the calls. You can run this script with minor modifications on Linux machine as well.
	-> On the CMD,
		$ python cucm_cdr_email_alerts.py
