from pickle import dump, load

with open('./db/people.db','wb') as file:
    dump([], file)
with open('./db/people.db','rb') as file:
    data = load(file)
print(data)

with open('./db/devices.db','wb') as file:
    dump({"d1":[2,[]]}, file)   
with open('./db/devices.db','rb') as file:
    data = load(file)   
     
with open('./db/cards.db','wb') as file: 
    dump('', file)  
with open('./db/logs.txt','w') as file: 
    file.write('')
print(data)
