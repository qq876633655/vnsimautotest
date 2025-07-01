import csv
with open("/home/visionnav/AGVServices/3dSlam/lastagvpose/agvpose1.csv",'r',encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)