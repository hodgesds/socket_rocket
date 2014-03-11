import json
import requests as r
res = r.get('http://localhost:8080', stream=True)

for line in res.iter_lines(chunk_size=1):
    data = json.loads(line)
    print data
