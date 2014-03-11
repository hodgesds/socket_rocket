import json
import requests as r
import redis
res = r.get('http://localhost:8080', stream=True)

rpub = redis.client.StrictRedis()

for line in res.iter_lines(chunk_size=30):
    data = json.loads(line)
    rpub.publish('master', line)
    print data
