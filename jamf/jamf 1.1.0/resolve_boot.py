'''
Copyright © 2020 Forescout Technologies, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from urllib.request import HTTPError, URLError

from xml.etree import ElementTree
boot_properties = ["filevault_status", "name", "size", "filevault_percent", "percentage_full"]

url = params["connect_jamf_url"]
url += "/JSSResource/computers/"
username = params["connect_jamf_username"]
password = params["connect_jamf_password"]
response = {}
if "dhcp_hostname" in params:
	url = url + "name/" + params["dhcp_hostname"]
elif "connect_globalprotect_computer_name" in params:
    url = url + "name/" + params["connect_globalprotect_computer_name"]
elif "mac" in params:
	uppercase_mac = params["mac"].upper()
	colon_mac = ":".join(uppercase_mac[i:i+2] for i in range(0,12,2))
	url = url + "macaddress/" + colon_mac
else:
	logging.error("Insufficient information to query.")

logging.info("The URL is: {}".format(url))
request = urllib.request.Request(url)
request.add_header("Authorization", "Basic %s" % jamf_lib.create_auth(username, password))
request.add_header("Accept", "application/xml")
try:
	resp = urllib.request.urlopen(request, context=ssl_context)
	properties = {}
	tree = ElementTree.fromstring(resp.read())
	logging.debug("The response from Jamf is {}".format(str(tree)))
	boot = {}
	for partition in tree.findall("hardware/storage/device/partitions/partition"):
		if partition.find("type").text == "boot":
			for prop in boot_properties:
				prop_value = partition.find(prop)
				if prop_value is not None:
					boot[prop] = prop_value.text
	properties["connect_jamf_boot_device"] = boot
	response["properties"] = properties
except HTTPError as e:
	response["error"] = "Could not resolve properties. Response code: {}".format(e.code)
except URLError as e:
	response["error"] = "Could not resolve properties. {}".format(e.reason)
except Exception as e:
	response["error"] = "Could not resolve properties. {}".format(str(e))
