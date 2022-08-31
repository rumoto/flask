import requests

HOST = 'http://127.0.0.1:5000'

response = requests.get(HOST)
print(response.status_code)
print(response.text)

response = requests.post(f'{HOST}/advertisements/', json={'title': 'title_1', 'description': 'description_1',
                                                         'owner': 'owner_1'})
print(response.status_code)
print((response.text))

response = requests.patch(f'{HOST}/advertisements/1', json={'title': 'title_1_v2'})
print(response.status_code)
print(response.text)

response = requests.get(f'{HOST}/advertisements/2')
print(response.status_code)
print(response.text)
#
response = requests.delete(f'{HOST}/advertisements/1')
print(response.status_code)
print(response.text)