# **Preprocess**
import pandas as pd
http = pd.read_csv("C:\\Users\\pranil\\Desktop\\burpy-master\\merge.csv")
from pycaret.clustering import *
clu1 = setup(data = http, normalize = True,numeric_features = ['single_q','double_q','dashes','braces','spaces','badwords'],ignore_features = ['method','path','body','class'])

kmeans = create_model('kmeans', num_clusters = 2)
kmeans
plot_model(kmeans)
plot_model(kmeans, plot = 'tsne')
kmeans_result = assign_model(kmeans)
merged_data = pd.concat([http, kmeans_result[['Cluster']]], axis=1)

# Save the merged data to CSV including the 'class' column
#merged_data.to_csv('/kmeans_result_with_class.csv', index=False)
import pandas as pd
test_http = pd.read_csv("C:\\Users\\pranil\\Desktop\\burpy-master\\test.csv")
test_http.head()
#pip install pycaret
from pycaret import *
from pycaret.clustering import predict_model

# 'test_http' is your dataset for prediction
test_result = predict_model(kmeans, data=test_http)
test_result.to_csv("E://DLA PROJECT//test_results")


from http.server import *
from urllib import request, error
import pandas as pd
from pycaret.clustering import*
import urllib.parse
import sys
badwords = ['sleep','drop','uid','select','waitfor','delay','system','union','order by','group by']
def ExtractFeatures(path):
  path = urllib.parse.unquote(path)
  badwords_count = 0
  single_q = path.count("'")
  double_q = path.count("\"")
  dashes = path.count("--")
  braces = path.count("(")
  spaces = path.count(" ")
  for word in badwords:
    badwords_count += path.count(word)
  lst = [single_q,double_q,dashes,braces,spaces,badwords_count]
  print(lst)
  return pd.DataFrame([lst],columns = ['single_q','double_q','dashes','braces','spaces','badwords','cluster'])
http = pd.read_csv("C:\\Users\\pranil\\Desktop\\burpy-master\\merge.csv")
clu1 = setup(data = http, normalize = True,numeric_features = ['single_q','double_q','dashes','braces','spaces','badwords'] , ignore_features = ['method','path','body','class'] )
kmeans = create_model('kmeans',num_clusters = 2)
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib import request, error
import sys

# Assuming ExtractFeatures is defined and functional
# Also assuming a KMeans model named 'kmeans' is trained previously

class SimpleHTTPProxy(SimpleHTTPRequestHandler):
    proxy_routes = {}

    @classmethod
    def set_routes(cls, proxy_routes):
        cls.proxy_routes = proxy_routes

    def do_GET(self):
        parts = self.path.split('/')
        print(parts)

        if len(parts) >= 4:
            live_data = ExtractFeatures(parts[3])  # Fixed typo: parts, not part
            result = predict_model(kmeans, data=live_data)
            print(result['Cluster'][0])
            if result['Cluster'][0] == "Cluster 1":
                print('Intrusion Detected')

        if len(parts) >= 3:
            self.proxy_request('http://' + parts[2] + '/')
        else:
            super().do_GET()

    def proxy_request(self, url):
        try:
            response = request.urlopen(url)
        except error.HTTPError as e:
            print('err')
            self.send_response_only(e.code)
            self.end_headers()
            return

        self.send_response_only(response.status)
        for name, value in response.headers.items():
            self.send_header(name, value)
        self.end_headers()
        self.copyfile(response, self.wfile)

SimpleHTTPProxy.set_routes({'proxy_route': 'http://demo.testfire.net/'})
with HTTPServer(('192.168.32.221', 8080), SimpleHTTPProxy) as httpd:
    host, port = httpd.socket.getsockname()
    print(f'Listening on http://{host}:{port}')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting")
        sys.exit(0)
