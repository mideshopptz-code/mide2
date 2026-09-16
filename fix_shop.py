# -*- coding: utf-8 -*- 
c = open("templates/shop/base.html", encoding="utf-8").read() 
c = c.replace('a href="/shop/bonus">Bonus', 'a href="/shop/missions">Missions</a><a href="/shop/bonus">Bonus') 
open("templates/shop/base.html", "w", encoding="utf-8").write(c) 
print("OK") 
