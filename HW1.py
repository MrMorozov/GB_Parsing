import requests
from pprint import pprint

# user MrMorozov token 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

user='MrMorozov'
token='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'
url='https://api.github.com/user/repos'


repos = requests.get(url, auth=(user, token))
for rep in repos.json():
    print(rep.get('name'))

