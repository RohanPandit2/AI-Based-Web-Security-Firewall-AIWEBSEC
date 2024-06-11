from rawweb import RawWeb
from xml.etree import ElementTree as ET
import urllib.parse
import base64
import csv

log_path = 'test1.log'

def parse_log(log_path):
    result = {}
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
        raw=raereq
        pass
    global headers, method, body, path
    headers = {}

    sp = raw.split('\r\n\r\n', 1)
    if len(sp) > 1:
        head = sp[0]
        body = sp[1]
    else:
        head = sp[0]
        body = ""
    c1 = head.split('\n', head.count('\n'))
    method = c1[0].split(' ', 2)[0]
    path = c1[0].split(' ', 2)[1]
    for i in range(1, head.count('\n') + 1):
        slice1 = c1[i].split(': ', 1)
        if slice1[0] != "":
            try:
                headers[slice1[0]] = slice1[1]
            except:
                pass
    return headers,method,body,path



f = open('httplog.csv', "w")
c = csv.writer(f)
c.writerow(["Method","Body","Path","Headers"])
f.close()
resultt = parse_log(log_path)


badwords = ['sleep','drop','uid','select','waitfor','delay','system','union','order by','group by']
def ExtractFeatures(method,path_enc,body_enc,headers):
    badwords_count=0
    path=urllib.unquote_plus(path_enc)
    body=urllib.unquote(body_enc)
    single_q = path.count("'")+body.count("'")
    double_q=path.count("\"")+body.count("\"")
    dashes=path.count("--")+body.count("--")
    braces=path.count("(")+body.count("(")
    spaces=path.count(" ")+body.count(" ")
    for word in badwords:
        badwords_count+=path.count(word)+body.count(word)
    for header in headers:
        badwords_count+=headers[header].count(word)+headers[header].count(word)\
    return [method,path_enc.encode('utf-8').strip(),body_enc.encode('utf-8').strip(),spaces,single_q,double_q,dashes,braces,badwords_count]



for items in resultt:
    raaww =base64.b64decode(items)
    headers,method,body,path = ParseRawHttpReq(raaww)
    resulttt=ExtractFeatures(method,path,body,headers)
    f = open('httplog.csv', "ab")
    c = csv.writer(f)
    c.writerow(resulttt)
    f.close()