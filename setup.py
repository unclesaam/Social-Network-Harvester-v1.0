import os, sys
import xml.etree.ElementTree as ET

SETTINGS_PATH = "SocialNetworkHarvester_v1p0\SocialNetworkHarvester_v1p0\settings.xml"

def cmd(c): 
	os.system(c)


def check_preriquisites():
	print("Checking preriquisites:")
	print("Detected system: %s"%sys.platform)
	if sys.platform != "win32":
		return False
	print("Detected python version: %i.%i"%(
		sys.version_info[0], sys.version_info[1]))
	if sys.version_info[0:2] != (3,4):
		return False
	return True

def install_dependencies():
	print("Will install the required dependencies:")
	try:
		for dependency in ["django==1.9.1","mysqlclient==1.3.4"]:
			cmd("pip install %s"%dependency)
	except:
		return False
	return True

def initial_snh_setup():
	print("Will now first-time-setup the SNH...")
	try:
		pass
	except:
		return False
	return True



def parse_settings():
	print("Will now parse the user-defined settings.")
	try:
		tree = ET.parse(SETTINGS_PATH)
		root = tree.getroot()
		root.find("SECRET_KEY").text = query_value("SecretKey",skippable=False, values=["test"])
		if query_value("", "Do you want to setup the Facebook app now?",values=['y','n']) == 'y':
			print("will now setup the facebook app.")

		tree.write(SETTINGS_PATH)
	except:
		print("An errror occured while parsing the user-defined settings")
		return False
	return True
	


def query_value(varName, queryText="Please specify a value for:", skippable=True, values=[]):
	print("%s"%queryText)
	inputVar = input("	%s %s: "%(varName,values if values else ""))
	if (not skippable and not inputVar) or (values and inputVar not in values):
		print("Invalid parameter.")
		return query_value(varName,queryText,skippable,values)
	return inputVar







if __name__ == "__main__":
	print("This setup tool is used to install Aspira on a windows machine, using a mysql server.")
	if 	check_preriquisites() and \
		install_dependencies() and \
		parse_settings() and \
		initial_snh_setup():
		print("Setup completed. You can now run the SNH with the command 'python manage.py runserver'")
	else:
		print(\
"""
Setup failed. Please make sure that you:
- Are running Windows v >= 7
- Are running Python 3.4
- Have mysql Community v5.7 installed
""")