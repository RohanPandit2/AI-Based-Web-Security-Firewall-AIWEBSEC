import http.client
import re
import gzip
from io import BytesIO

class RawWeb:
    def __init__(self, raw):
        try:
            raw = raw.decode('utf8')
        except Exception:
            pass

        self.headers = {}
        sp = raw.split('\n\n', 1)
        if len(sp) > 1:
            head = sp[0]
            self.body = sp[1]
        else:
            head = sp[0]
            self.body = ""
        c1 = head.split('\n', head.count('\n'))
        self.method = c1[0].split(' ', 2)[0]
        self.path = c1[0].split(' ', 2)[1]
        for i in range(1, head.count('\n') + 1):
            slice1 = c1[i].split(': ', 1)
            if slice1[0] != "":
                self.headers[slice1[0]] = slice1[1]

    def rebuild(self, method, path, code, headers, body):
        raw_stream = f"{method} {path} {code}\n"
        for key, value in headers.items():
            raw_stream += f"{key}: {value}\n"
        raw_stream += f"\n{body}"
        return raw_stream

    def addheaders(self, new_header):
        for key, value in new_header.items():
            self.headers[key] = value
        return self.rebuild(self.method, self.path, "HTTP/1.1", self.headers, self.body)

    def removeheaders(self, rem_headers):
        for header in rem_headers:
            if header in self.headers:
                del self.headers[header]
        return self.rebuild(self.method, self.path, "HTTP/1.1", self.headers, self.body)

    def addparameters(self, new_params):
        new_body = self.body[:-1]
        for key, value in new_params.items():
            new_body += f"&{key}={value}"
        return self.rebuild(self.method, self.path, "HTTP/1.1", self.headers, new_body)

    def removeparameter(self, del_param):
        rx = f'(^|&){del_param}=[^&]*'
        new_body = re.sub(rx, '', self.body)
        self.body = new_body
        return self.rebuild(self.method, self.path, "HTTP/1.1", self.headers, new_body)

    def changemethod(self):
        url = self.path
        if self.method == "POST":
            if "Content-Type" in self.headers:
                del self.headers['Content-Type']
            if "=" in url:
                url += "&"
            else:
                url += "?"
            url += self.body[:-1]
            self.body = ""
            self.method = "GET"
            self.path = url
            return self.rebuild("GET", url, "HTTP/1.1", self.headers, self.body)
        else:
            self.headers['Content-Type'] = 'www.demo.testfire.net'
            a = url.split('?', 1)
            url = a[0]
            self.method = "POST"
            self.path = url
            self.body = a[1]
            return self.rebuild("POST", url, "HTTP/1.1", self.headers, self.body)

    def craft_res(self, res_head, res_body):
        for i in range(len(res_head)):
            e1 = res_head[i]
            if e1[1] == "gzip":
                res_body = self.decode_gzip(res_body)
        return res_body

    def decode_gzip(self, compresseddata):
        compressedstream = BytesIO(compresseddata)
        gzipper = gzip.GzipFile(fileobj=compressedstream)
        return gzipper.read()

    def fire(self, ssl):
        if len(self.path) > 70:
            print('[+]', self.method, self.path[:100] + "...")
        else:
            print('[+]', self.method, self.path)
        if ssl == "on":
            con = http.client.HTTPSConnection('demo.testfire.net')
        else:
            con = http.client.HTTPConnection('demo.testfire.net')
        try:
            con.request(self.method, self.path, self.body, self.headers)
            res = con.getresponse()
        except Exception:
            print('[+] Connectivity Issue ')
            return 'Error', 'Error', {}, 'Error'

        res_headers = {}
        for i in range(len(res.getheaders())):
            res_headers[res.getheaders()[i][0]] = res.getheaders()[i][1]
        return res.status, res.reason, res_headers, self.craft_res(res.getheaders(), res.read())
