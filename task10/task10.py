import csv

import subprocess


domains = [
    "google.com",
    "yandex.ru", 
    "github.com",
    "stackoverflow.com",
    "rutube.com"
]

data = [['IP', 'TTL', 'RTT', 'Count package', 'Traceroute']]

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

    for word_of_ping in result.stdout.split():
        ping.append(word_of_ping)

        if(count-2>=0 and ping[count-2] == "Среднее"):
            Rtt = str(word_of_ping)

        if(count-2>=0 and ping[count-2] == "Ответ" and Ip == ""):
            Ip = str(word_of_ping[:-1])

        if(word_of_ping[0:3] == "TTL" and Ttl == ""):
            Ttl = str(word_of_ping[4:])

        if(count-2>=0 and ping[count-2] == "отправлено" and Count_package == ""):
            Count_package = str(word_of_ping[:-1])
            
        count+=1
    
    traceroute_result = ""
    if Ip:
        trace = subprocess.run(
            ["tracert", "-h", "3", Ip],
            capture_output=True,
            text=True,
            encoding='cp866'
        )
        traceroute_result = "\n".join(trace.stdout.split("\n"))
    
    data.append([Ip, Ttl, Rtt, Count_package, traceroute_result])

with open('task1_output.csv', 'w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data)