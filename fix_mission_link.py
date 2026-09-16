# -*- coding: utf-8 -*- 
c = open("templates/base.html", encoding="utf-8").read() 
c = c.replace('a href="/zones">Zones', 'a href="/missions">Missions</a><a href="/zones">Zones') 
open("templates/base.html", "w", encoding="utf-8").write(c) 
print("OK") 
