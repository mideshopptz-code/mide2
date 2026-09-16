# -*- coding: utf-8 -*- 
content = open("templates/base.html", encoding="utf-8").read() 
old = "Profile" 
if old in content and "dashboard" not in content: 
    content = content.replace("Profile", "Dashboard Profile") 
    open("templates/base.html", "w", encoding="utf-8").write(content) 
    print("base.html updated") 
else: 
    print("nothing to do") 
print("DONE") 
