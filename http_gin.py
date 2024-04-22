import requests

# кушетка на 2 часа
url2 = 'https://dikidi.ru/ru/record/658559?p=4.pi-po-sm-ss-sd-cf&o=1&m=1505101&s=5917203&d=202404211805&r=682591330&rl=0_682591330&sdr=&source=widget'
# кушетка на 4 часа
url = 'https://dikidi.ru/ru/record/658559?p=4.pi-po-sm-ss-sd&o=1&m=1505101&s=5918559&rl=0_0&source=widget'


response = requests.get(url)

if response.status_code == 200:
    print(response.text)
else:
    print('Failed to retrieve the webpage')

