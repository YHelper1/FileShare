import socket
f = open("properties.txt", "r")
mas = []
for i in f.readlines():
    mas.append(i[i.find(" "):])
f.close()

