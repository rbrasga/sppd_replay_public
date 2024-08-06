import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender_email = "<email address>"
password = '<password>'

def sendBracketUpdate(receiver_emails,team_name,delta_data,new_bracket_data):
	message = MIMEMultipart("alternative")
	message["Subject"] = f"[SPPDReplay] {team_name} - Bracket Update"
	message["From"] = sender_email
	message["To"] = sender_email
	
	html_content='''\
	<html>
	<head>
	<style>
	table {
	  font-family: arial, sans-serif;
	  width: 100%;
	}

	td, th {
	  text-align: center;
	  padding: 8px;
	}
	</style>
	</head>
	<body>
	'''
	html_content=f'''\
	<h2>Teamwar Bracket Change</h2>
	<table border ="1">
	  <tr
		<th>Team Name</th>
		<th>Score</th>
		<th>Runs</th>
		<th>Average</th>
	  </tr>
	  <tr>
		<td>{team_name}</td>
		<td>{delta_data[0]}</td>
		<td>{delta_data[1]}</td>
		<td>{delta_data[2]}</td>
	  </tr>
	</table>
	<br>
	<h2>Teamwar Bracket Data</h2>
	<table>
	  <tr>
		<th>Team Name</th>
		<th>Score</th>
		<th>Runs</th>
		<th>Average</th>
		<th>Members</th>
		<th>Projected</th>
		<th>Maximum</th>
	  </tr>
	'''
	BRACKETID=None
	for team_data in new_bracket_data:
		if BRACKETID == None: BRACKETID = team_data[7]
		html_content+=f'''\
		  <tr>
			<td>{team_data[0]}</td>
			<td>{team_data[1]}</td>
			<td>{team_data[2]}</td>
			<td>{team_data[3]}</td>
			<td>{team_data[4]}</td>
			<td>{team_data[5]}</td>
			<td>{team_data[6]}</td>
		  </tr>
		'''
	link = f"https://sppdreplay.net/brackets/{BRACKETID}"
	html_content+=f'''\
	</table>
	<br>
	<h5>Please consider a 1$ donation per month for these services. Either to me - or your favorite charity and share your receipt.</h5>
	<h5>To Unsubscribe, login into sppdreplay with your email address and navigate to <a href="{link}">SPPD Replay Bracket {BRACKETID}</a>. Select Subscribe: Yes -> No.</h5>
	</body>
	</html>
	'''

	# Turn these into plain/html MIMEText objects
	html_part = MIMEText(html_content, "html")

	# Add HTML/plain-text parts to MIMEMultipart message
	# The email client will try to render the last part first
	message.attach(html_part)
	try:
		# Create secure connection with server and send email
		context = ssl.create_default_context()
		with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
			server.login(sender_email, password)
			server.sendmail(
				sender_email, receiver_emails, message.as_string()
			)
	except:
		print("\n\n[Error] Unable to send email\n")