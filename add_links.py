# -*- coding: utf-8 -*- 
c = open("templates/base.html", encoding="utf-8").read() 
if "Dashboard" not in c: 
    c = c.replace("Profile", "Dashboard Profile") 
    open("templates/base.html", "w", encoding="utf-8").write(c) 
    print("OK base.html") 
else: 
    print("base already updated") 
print("DONE") 
