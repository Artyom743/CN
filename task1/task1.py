import subprocess
import csv


domains = [
    "google.com",
    "yandex.ru", 
    "github.com",
    "stackoverflow.com",
    "rutube.com",
    "vk.com",
    "mail.ru",
    "habr.com",
    "wikipedia.org",
    "mail.ru"
]

data = [['IP', 'TTL', 'RTT', 'Count package']]

for domain in domains:
    result = subprocess.run(
        ["ping", domain], 
        capture_output=True, 
        text=True, 
        encoding='cp866')
    
    ping = []
    count = 0
    Rtt = "" 
    Ttl = ""
    Count_package = ""
    Ip = ""

    for line_of_ping in result.stdout.split():
        ping.append(line_of_ping)

        if(count-2>=0 and ping[count-2] == "Среднее"):
            Rtt = str(line_of_ping)

        if(count-2>=0 and ping[count-2] == "Ответ" and Ip == ""):
            Ip = str(line_of_ping[:-1])

        if(line_of_ping[0:3] == "TTL" and Ttl == ""):
            Ttl = str(line_of_ping[4:])

        if(count-2>=0 and ping[count-2] == "отправлено" and Count_package == ""):
            Count_package = str(line_of_ping[:-1])
            
        count+=1
    data.append([Ip, Ttl, Rtt, Count_package])

with open('task1_output.csv', 'w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data)
    



