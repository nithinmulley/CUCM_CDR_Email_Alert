#!/usr/bin/python3
###############################################################################
# This Script searches for 911 calls in the CDR Dump and sends an email alert #
# with the required details. It can also check GW names and send alert only   #
# to the site specific personnel. CUCM AXL is used to get the Device and Line #
# descriptions which are not generally provided in the raw CDR.               #
###############################################################################
import os
import shutil
import csv
import time
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl
from six.moves import urllib
from suds.transport.https import HttpAuthenticated
from suds.client import Client

###############################################################################
# Change all the variables here accordingly
# CUCM AXL Credentials
axl_user = 'axl_user'
axl_pswd = 'axl_pswd'
CUCM_site = 'https://10.10.10.10/axl/'

# WSDL location
wsdl = 'file:///D:/axl_schemaCM10.5/AXLAPI.wsdl'

# Directory where CDR dumps new CDRs
path = r'D:\CDR_new'

# Directory where CDR dumps will be moved after being processed
archive_path = r'D:\CDR_archive'

# CSV file log of all the Emergency Calls for a quick reference
file_log_911 = r'D:\CDR_MHC_Mega_Cluster\file_log_911_Mega.csv'

# Change current working directory to new CDR dump location
os.chdir(path)

# Relay server for email alerts
realy_server = '10.10.10.91'

# Default Email From address for all Email alerts
email_from_default = "cdr_alert@xyz.xyz"

# def -> Default Email destination, Change Email addresses for other locations
email_dict = {
                'def': ['nit.tin@xyz.xyz'],
                'CP101': ['mart.ian@xyz.xyz', 'nit.tin@xyz.xyz'],
                'MN201': ['meg.han@xyz.xyz', 'nit.tin@xyz.xyz'],
            }
###############################################################################

# Create SSL Context
ssl_def_context = ssl.create_default_context()
ssl_def_context.check_hostname = False
ssl_def_context.verify_mode = ssl.CERT_NONE
ssl_def_context.options = ssl.OP_CIPHER_SERVER_PREFERENCE
ssl_def_context.set_ciphers('HIGH')

#############################################
# Send e-Mail                               #
#############################################


def send_mail(email_content, email_subject, via, partition):
    email_from = email_from_default
    email_to = email_dict.get('def')
    # Check if the call made out via a Gateway, only then notify site specific personnel
    if len(via) > 5:
        for site_code in email_dict:
            # GW names or partition names are checked here to send emails to specific personnel
            if site_code in via or site_code in partition:
                email_to = email_dict.get(site_code)
    email_msg = MIMEMultipart('alternative')
    email_msg['Subject'] = email_subject
    email_msg['From'] = email_from
    email_msg['To'] = ", ".join(email_to)
    email_body = MIMEText(email_content, 'html')
    email_msg.attach(email_body)
    email_server = smtplib.SMTP('172.16.32.111')
    email_server.sendmail(email_from, email_to, email_msg.as_string())
    email_server.quit()
    return


while 1:
    cdr_files = [file for file in os.listdir(path) if file.startswith('cdr')]
    cdr_list = []
    rem_cdr_list = []
    for file in cdr_files:
        try:
            os.rename(os.path.abspath(file), os.path.abspath(file)+'_')
            os.rename(os.path.abspath(file)+'_', os.path.abspath(file))
            with open(file, 'r') as f:
                reader = csv.reader(f)
                file_cdr = list(reader)
                del file_cdr[0:1]
                cdr_list.extend(file_cdr)
            rem_cdr_list.append(file)
        except:
            pass

    for data in cdr_list:
        if data[29] == '911' or data[29] == '9911':
            t = HttpAuthenticated(username=axl_user, password=axl_pswd)
            t.handler = urllib.request.HTTPBasicAuthHandler(t.pm)
            t1 = urllib.request.HTTPSHandler(context=ssl_def_context)
            t.urlopener = urllib.request.build_opener(t.handler, t1)
            client = Client(wsdl, location=CUCM_site, transport=t)
            device_description = "Unavailable"
            line_description = "Unavailable"
            try:
                device_details = client.service.getPhone(name=data[56])
                if device_details['return']['phone']['description']:
                    device_description = device_details['return']['phone']['description']
                try:
                    for j in device_details['return']['phone']['lines']['line']:
                        if j['dirn']['pattern'] == data[8]:
                            if j['display']:
                                line_description = j['display']
                except:
                    line_description = "Unavailable"
            except:
                device_description = "Unavailable"
            call_time = datetime.datetime.fromtimestamp(int(data[48] if int(data[47]) == 0 else data[47]))
            call_duration = datetime.timedelta(seconds=int(data[55]))
            with open(file_log_911, 'a') as f_log:
                file_csv_write = csv.writer(f_log, lineterminator='\n')
                file_csv_write.writerow([call_time, data[8], data[29], call_duration, data[56], data[57], data[53]])
            print(\
            '''
            Call Alert\n
             Date and Time: {call_time}
            Calling Number: {data[8]}
             Called Number: {data[29]}
                  Duration: {call_duration}
               Device Name: {data[56]}
        Device Description: {device_description}
          Line Description: {line_description}
                       via: {data[57]}
             Out Partition: {data[53]}
            '''.format(**locals()))
            email_content = """
            <!DOCTYPE html>
            <html>
                <head>
                    <style>
                        .title-text {{
                            color: black;
                            text-decoration: underline;
                            font-family: monospace;
                            font-size: 18px;
                            text-shadow: 1px 1px 1px #aaa;
                            }}
                        .footer-text {{
                            font-family: monospace;
                            color: black;
                            font-size: 12px;
                            }}
                        table#t101 {{
                            color: blue;
                            border: 1px solid black;
                            border-collapse: collapse;
                            font-family: "Lucida Console";
                            font-size: 14px;
                            width:450px;
                            height:250px;
                            background-color: white;
                            }}
                        table#t101 tr:nth-child(even) {{
                            background-color: #eeeeee;
                            }}
                        table#t101 tr:nth-child(odd) {{
                            background-color: #ffffff;
                            }}
                        table#t101 td {{
                            border: 1px solid black;
                            border-collapse: collapse;
                            }}
                    </style>
                </head>
                <body bgcolor= "#ffffaf">
                    <h2 class='title-text'>Emergency Call Alert Service</h2>
                    <div>
                        <table id="t101">
                            <tr>
                                <td>Date and Time</td>
                                <td>{call_time}</td>
                            </tr>
                                <td>Calling Number</td>
                                <td>{data[8]}</td>
                            <tr>
                                <td>Called Number</td>
                                <td>{data[29]}</td>
                            </tr>
                            <tr>
                                <td>Duration</td>
                                <td>{call_duration}</td>
                            </tr>
                            <tr>
                                <td>Line Description</td>
                                <td>{line_description}</td>
                            </tr>
                            <tr>
                                <td>Device Description</td>
                                <td>{device_description}</td>
                            </tr>
                            <tr>
                                <td>Device Name</td>
                                <td>{data[56]}</td>
                            </tr>
                            <tr>
                                <td>via</td>
                                <td>{data[57]}</td>
                            </tr>
                            <tr>
                                <td>Out Partition</td>
                                <td>{data[53]}</td>
                            </tr>
                        </table> 
                    </div>
                    <div>
                        <p class="footer-text">This is an automated alert for the emergency calls made from your 
                        site/building. If you have any queries, please do reply back.</p>
                    </div>
                </body>
            </html>
            """.format('Date and Time', 'Calling Number', 'Called Number', 'Duration', 'Line Description',
                       'Device Description', 'Device Name', 'via', 'Out Partition', **locals())
            email_subject = "**Emergency Call Alert"
            send_mail(email_content, email_subject, data[57], data[53])


# Archive CDR Files
    for rm_file in rem_cdr_list:
        path1 = os.path.abspath(rm_file)
        path2 = os.path.join(archive_path, rm_file)
        try:
            shutil.move(rm_file, path2)
            print('Moved {rm_file}'.format(**locals()))
        except:
            pass
        
# Archive CMR Files
    cmr_files = [file for file in os.listdir(path) if file.startswith('cmr')]
    for rm_file in cmr_files:
        path2 = os.path.join(archive_path, rm_file)
        try:
            shutil.move(rm_file, path2)
            print('Moved {rm_file}'.format(**locals()))
        except:
            print('unable to move {rm_file}'.format(**locals()))
    time.sleep(90)
