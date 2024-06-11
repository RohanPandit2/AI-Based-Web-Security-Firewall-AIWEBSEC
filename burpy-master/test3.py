from xml.etree import ElementTree as ET
import urllib.parse
import base64
import csv

log_path = 'test1.log'




def parse_log(log_path):
    try:
        with open(log_path, 'r', encoding='utf-8') as file:
            xml_data = file.read()
    except IOError:
        print("[+] Error!!! ", log_path, "doesn't exist..")
        exit()

    try:
        tree = ET.ElementTree(ET.fromstring(xml_data))
    except Exception as e:
        print("[+] Oops..! Please make sure there's no binary data in the log (e.g., raw image dumps or flash files).")
        exit()

    result = {}
    root = tree.getroot()
    for reqs in root.findall('item'):
        raw_req = reqs.find('request').text
        raw_req = urllib.parse.unquote(raw_req)
        raw_resp = reqs.find('response').text
        result[raw_req] = raw_resp

    return result

def ParseRawHttpReq(raereq):
    try:
        raw = raereq.decode('utf8')
    except Exception as e:
        raw = raereq
    headers = {}
    sp = raw.split("\r\n\r\n\r\n",1)
    if sp[1] != "":
        head = sp[0]
        body = sp[1]
    else:
        head = sp[0]
        body = ""
    c1 = head.split('\n')
    method = c1[0].split(' ', 2)[0]
    path = c1[0].split(' ', 2)[1]
    for line in c1[1:]:
        slice1 = line.split(': ', 1)
        if slice1[0] != "":
            try:
                headers[slice1[0]] = slice1[1]
            except:
                pass
    return headers, method, body, path

resultt = parse_log(log_path)

with open('httplog2.csv', "w", newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Method", "Body", "Path", "Headers"])
    for items in resultt:
        data=[]
        raaww = base64.b64decode(items)
        headers, method, body, path = ParseRawHttpReq(raaww)
        data.extend(method)
        data.extend(body)
        data.append(path)
        data.append(headers)
        writer.writerows(data)
