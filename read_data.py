from pickle import dump, load

with open('./db/devices.db','rb') as file:
    data = load(file)    
print('devices: ',data)
with open('./db/people.db','rb') as file:
    data = load(file)    
print('people: ',data)
with open('./db/cards.db','rb') as file:
    data = []
    while True:
        try:
            data.append(load(file))
        except EOFError:
            break
               
print('cards: ',data)