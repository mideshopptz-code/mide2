# -*- coding: utf-8 -*- 
c = open("templates/base.html", encoding="utf-8").read() 
c = c.replace('a href="/profile">Dashboard Profile</a>', 'a href="/dashboard">Dashboard</a><a href="/kpi">KPI</a><a href="/zones">Zones</a><a href="/profile">Profile</a>') 
open("templates/base.html", "w", encoding="utf-8").write(c) 
print("OK") 
