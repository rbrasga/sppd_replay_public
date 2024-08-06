import paramiko
import re

fh = open('SSHKEYS.txt',"r")
result = fh.read()
split_result = result.split(",")
UNAME = split_result[0]
PWORD = split_result[1]
print(f'SSHKEYS: {UNAME},{PWORD}')
CLOUD_SERVER='<ip address 1>'
#CLOUD_SERVER='<ip address 2>'

def setupTeamManager(email,password):
	match = re.match("^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$", email, re.I)
	if match == None:
		return False, "That's not a valid email address"
	password = password.replace('"','')
	if password == "":
		return False, "You forgot to enter a password"
	email = email.lower()
	# dots don't matter in gmail addresses
	if "gmail.com" in email:
		split_email = email.split('@')
		email = split_email[0].replace('.','') + "@" + split_email[1]
	global UNAME,PWORD
	# Connect
	client = paramiko.SSHClient()
	client.load_system_host_keys()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect(CLOUD_SERVER, username='user', password='TeamManager123')
	# Run a command (execute PHP interpreter)
	stdin, stdout, stderr = client.exec_command(f'python SPPD_Team_Manager_linux_MTO.py --email {email} --password "{password}"')
	#print(type(stdin))  # <class 'paramiko.channel.ChannelStdinFile'>
	#print(type(stdout))  # <class 'paramiko.channel.ChannelFile'>
	#print(type(stderr))  # <class 'paramiko.channel.ChannelStderrFile'>

	# Optionally, send data via STDIN, and shutdown when done
	#stdin.write(email)
	#time.sleep(1)
	#stdin.write(password)
	#stdin.channel.shutdown_write()
	#If it was a success. Add it, then restart all.

	# Print output of command. Will wait for command to finish.
	#print(f'STDOUT: {stdout.read().decode("utf8")}')
	#print(f'STDERR: {stderr.read().decode("utf8")}')
	stdout_result = stdout.read().decode("utf8")
	stderr_result = stderr.read().decode("utf8")
	'''
	Added masterToken, USERNAME: sppd.2020.7@gmail.com: You don't need a password to login anymore.
	Updated OAUTH_EXPIRATION: 2021-03-13 07:01:25, USERNAME: sppd.2020.7@gmail.com
	Updated UBI_EXPIRATION: 2021-03-13 09:21:26, USERNAME: sppd.2020.7@gmail.com
	'''
	success = "Updated OAUTH_EXPIRATION" in stdout_result and "Updated UBI_EXPIRATION" in stdout_result
	# Get return code from command (0 is default for success)
	#print(f'Return code: {stdout.channel.recv_exit_status()}')

	# Because they are file objects, they need to be closed
	stdin.close()
	stdout.close()
	stderr.close()
	# Close the client itself
	client.close()
	if success:
		client = paramiko.SSHClient()
		client.load_system_host_keys()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect(CLOUD_SERVER, username=UNAME, password=PWORD)
		# Run a command (execute PHP interpreter)
		stdin, stdout, stderr = client.exec_command("cd sppd_team_source/ && sudo sh -c './rebuild.sh'")
		override_string = ""
		tmp_result = stdout.read().decode("utf8")
		if "FOUNDABC123" in tmp_result:
			override_string = "Stop, you're account has already been added."
		# Because they are file objects, they need to be closed
		stdin.close()
		stdout.close()
		stderr.close()
		# Close the client itself
		client.close()
		if override_string != "":
			return True, override_string
	else:
		client = paramiko.SSHClient()
		client.load_system_host_keys()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect(CLOUD_SERVER, username=UNAME, password=PWORD)
		# Run a command (execute PHP interpreter)
		stdin, stdout, stderr = client.exec_command("sudo sh -c 'echo > /home/user/MASTERTOKEN.txt'")
		# Because they are file objects, they need to be closed
		stdin.close()
		stdout.close()
		stderr.close()
		# Close the client itself
		client.close()
	long_string = ""
	long_string += f"{stdout_result}\n"
	long_string += f"{stderr_result}"
	return success, long_string
		