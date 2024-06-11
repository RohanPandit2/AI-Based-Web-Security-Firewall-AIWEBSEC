from xml.etree import ElementTree as ET
import urllib.parse
import base64
import csv

log_path = 'geeksforgeeks1.log'


def parse_log(log_path):
    try:
        with open(log_path, 'r', encoding='utf-8') as file:
            xml_data = file.read()
    except FileNotFoundError:
        print(f"[+] Error!!! {log_path} doesn't exist..")
        exit()

    try:
        tree = ET.ElementTree(ET.fromstring(xml_data))
    except ET.ParseError:
        print("[+] Oops..! Please make sure there's no binary data in the log (e.g., raw image dumps or flash files).")
        exit()

    result = {}
    root = tree.getroot()
    for reqs in root.findall('item'):
        raw_req = urllib.parse.unquote(reqs.find('request').text)
        raw_resp = reqs.find('response').text
        result[raw_req] = raw_resp

    return result


def parse_raw_http_req(raereq):
    try:
        raw = raereq.decode('utf8')
    except (AttributeError, UnicodeDecodeError):
        raw = raereq

    headers = {}
    sp = raw.split('\r\n\r\n', 1)
    head, body = sp if len(sp) > 1 else (sp[0], "")

    method, path = head.split(' ', 2)[:2]

    for line in sp[1:]:
        slice1 = line.split(': ', 1)
        if slice1[0] != "":
            try:
                headers[slice1[0]] = slice1[1]
            except IndexError:
                pass

    return headers, method, body, path


badwords = ['sleep', 'drop', 'uid', 'select', 'waitfor', 'delay', 'system', 'union', 'order by', 'group by']


def extract_features(method, path_enc, body_enc, headers):
    path = path_enc
    body = body_enc
    single_q = path.count("'") + body.count("'")
    double_q = path.count("\"") + body.count("\"")
    dashes = path.count("--") + body.count("--")
    braces = path.count("(") + body.count("(")
    spaces = path.count(" ") + body.count(" ")

    badwords_count = sum(path.count(word) + body.count(word) for word in badwords)
    badwords_count += sum(header_value.count(word) for header_value in headers.values() for word in badwords)

    return [method, path_enc.encode('utf-8').strip(), body_enc.encode('utf-8').strip(), single_q, double_q, dashes,
            braces, spaces, badwords_count, "1"]


resultt = parse_log(log_path)

with open('httplog.csv', "w", newline='') as file:
    c = csv.writer(file)
    c.writerow(["Method", "Path", "Body", "single_q", "double_q", "dashes", "braces", "spaces", "badwords", "class"])

    for items in resultt:
        raaww = base64.b64decode(items)
        headers, method, body, path = parse_raw_http_req(raaww)
        resulttt = extract_features(method, path, body, headers)
        c.writerow(resulttt)
