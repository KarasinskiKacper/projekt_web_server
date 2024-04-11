from pickle import dump, load

with open('./db/people.db','wb') as file:
    dump([("Adam", "1234",'qwe',1),(("Tom", None,None,3))], file)
with open('./db/people.db','rb') as file:
    data = load(file)
print(data)

with open('./db/devices.db','wb') as file:
    dump({"d1":[2,[]]}, file)   
with open('./db/devices.db','rb') as file:
    data = load(file)   
     
with open('./db/cards.db','ab') as file: 
    file.truncate(0)
    dump('abc',file)
    dump('acb',file)
    dump('cba',file)
print(data)
