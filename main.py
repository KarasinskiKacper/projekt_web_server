from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pickle import dump, load
from datetime import datetime

port=80
server_address = ('', port)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path=='/':
            content_length = int(self.headers['Content-Length'])
            req = self.rfile.read(content_length).decode().split('&')
            qc = {}
            for e in req:
                key,value = e.split('=')
                qc[key]=value
            
            if len(qc):
                if 'name' in qc.keys() and 'access_lvl' in qc.keys() and 'code' in qc.keys() and 'card' in qc.keys(): 
                    if qc['code'] == '':
                        qc['code'] = None
                    if qc['card'] == '':
                        qc['card'] = None
                    is_new = True
                    with open('./db/people.db','rb') as file:
                        data = load(file)

                    index = 0
                    codes = []
                    cards = []
                    used_code = ''
                    used_card = ''
                    for name, code, card, access_lvl in data:
                        if name==qc['name']:
                            is_new = False
                            used_code = code
                            used_card = card
                        if is_new:       index += 1
                        if code != None: codes.append(code)
                        if card != None: cards.append(card)
                    if used_code != '' and used_code != None: codes.remove(used_code)
                    if used_card != '' and used_card != None: cards.remove(used_card)
                    if qc['card'] != None and qc['card'] != used_card:
                        with open('./db/cards.db','rb') as file:
                            cards_to_save = []
                            while True:
                                try:
                                    x = load(file)
                                    if x != qc['card']: cards_to_save.append(x)
                                except EOFError:
                                    break
                        # with open('./db/cards.db','wb') as file:
                        #     dump('',file)
                        with open('./db/cards.db','ab') as file:
                            file.truncate(0)
                            for card_to_save in cards_to_save:
                                dump(card_to_save, file)
                    
                    if qc['code'] not in codes and qc['card'] not in cards and (qc['code'] == None or len(qc['code'])==4) and int(qc['access_lvl'])>0:
                        if is_new:
                            data.append((qc['name'], qc['code'], qc['card'], int(qc['access_lvl'])))
                            with open('./db/people.db','wb') as file:
                                dump(data, file)
                        else:
                            data[index]=(qc['name'], qc['code'], qc['card'], int(qc['access_lvl'])) 
                            with open('./db/people.db','wb') as file:
                                dump(data, file)
                        self.do_GET("Added/changed person")       
                    else:
                        self.do_GET("Wrong data")       
                           
                elif 'person-to-delete' in qc.keys():
                    with open('./db/people.db','rb') as file:
                        data = load(file)
                    new_data = [(name, code, card, access_lvl) for name, code, card, access_lvl in data if name != qc['person-to-delete']]
                    if len(new_data)!=len(data):
                        with open('./db/people.db','wb') as file:
                            dump(new_data, file)
                        self.do_GET(f"Removed {qc['person-to-delete']}")
                    else:
                        self.do_GET("Wrong data") 
                        
                # ------------ device -----------------
                elif 'device-access-level' in qc.keys():
                    if int(qc['device-access-level']) > 0:
                        with open('./db/devices.db','rb') as file:
                            data = load(file)
                        data['d1'] = [int(qc['device-access-level']), data['d1'][1]]
                        with open('./db/devices.db','wb') as file:
                            dump(data, file)
                        self.do_GET(f"Changed device's access level to: {qc['device-access-level']}")
                    else:
                        self.do_GET("Wrong data") 
                elif 'personal-access-' == list(qc.keys())[0][:16]:
                    with open('./db/devices.db','rb') as file:
                            data = load(file)
                    data['d1'] = [data['d1'][0], []]
                    
                    for value in qc.values():
                        data['d1'][1].append(value)
                        
                    with open('./db/devices.db','wb') as file:
                        dump(data, file)
                    
                    self.do_GET("Change device's personal access")
                else:
                    self.send_response(400)
                    
    def do_GET(self, res=''):
        if self.path == '/':
            with open('./db/devices.db','rb') as file:
                device_data = load(file)
            device_access_level = device_data['d1'][0]
            device_personal_access = device_data['d1'][1]
            
            with open('./db/people.db','rb') as file:
                data = load(file)
            people_data = "".join([f"<li>Name: {name:>10}, code: {code}, card: {card}, access lvl: {access_lvl}</li>" for name, code, card, access_lvl in data])
            
            with open('./db/cards.db','rb') as file:
                card_data = []
                while True:
                    try:
                        card_data.append(load(file))
                    except EOFError:
                        break
            cards = '<option value="" >None</option>'
            cards += "".join([f'<option value="{value}">{value}</option>' for value in card_data])
            cards += '<option value="" disabled>-----------</option>'
            card_data2=[]
            for name, code, card, access_lvl in data:
                if card != None:
                    card_data2.append(card)
            cards += "".join([f'<option value="{value}">{value}</option>' for value in card_data2])
            
            people_to_delete = '<option value="" selected="true" disabled>None</option>'
            people_to_delete += "".join([f'<option value="{name}">{name}</option>' for name, code, card, access_lvl in data])
            
            personal_access = "".join([
                f'<input type="checkbox" id="personal-access-{name}" name="personal-access-{name}" value="{name}" {"checked" if name in device_personal_access else ""} ><label for="personal-access-{name}">{name}</label><br>'
                for name, code, card, access_lvl in data if access_lvl < device_access_level or name in device_personal_access
            ])

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"""
                <!DOCTYPE html>
                <html lang="pl">

                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Server</title>
                </head>

                <body style='font-family: sans-serif;'>
                    <h1>People:</h1>
                    <ol>
                        {people_data}
                    </ol>
                    <div style='display: flex; margin-bottom: 20px;'>
                        <div style='margin-right:20px;'>
                            <h2>Add or change person:</h2>
                            <form action="/" method="post">
                                <label for="name">Name: </label><br>
                                <input type="text" id="name" name="name" autocomplete="off" required><br>
                                <label for="code">Code: </label><br>
                                <input type="text" id="code" name="code" autocomplete="off"><br>
                                <label for="cards">Card: </label><br>
    
                                <select id="cars" name="card">
                                    {cards}
                                </select><br>
                                <label for="access_lvl">Access level:</label><br>
                                <input type="number" id="access_lvl" name="access_lvl" required><br><br>
                                <input type="submit" value="add/change"  >
                            </form>
                        </div>
                        <div>
                            <h2>Remove person:</h2>
                            <form action="/" method="post">
                                <label for="person-to-delete">Name: </label><br>
                                <select id="person-to-delete" name="person-to-delete" required>
                                    {people_to_delete}
                                </select><br><br>
                                <input type="submit" value="remove"  >
                            </form>
                        </div>
                    </div>
                    <h1>Devices:</h1>
                        <div style='display: flex;'>
                            <div>
                                <h2>Change device's access level:</h2>
                                <form action="/" method="post">
                                    <label for="device-access-level">New access level:</label><br>
                                    <input type="number" id="device-access-level" name="device-access-level" required><br><br>
                                    <input type="submit" value="Change" >
                                </form>
                            </div>
                            <div>
                                <h2>Change device's personal access:</h2>
                                <form action="/" method="post">
                                    {personal_access}<br>
                                    <input type="submit" value="Change" >
                                </form>
                            </div>
                        </div>
                    <p>{res}</p>
                </body>
                </html>
            """.encode())
        
        elif self.path.startswith('/check-code'):
            query_components = parse_qs(urlparse(self.path).query)
            code = query_components['code'][0]
            device_id = query_components['id'][0]
        
            check = self.check_code(code, device_id)
            if check:
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"ok") #TODO remove
            else:
                self.send_response(401)
                self.send_header('WWW-authenticate', 'Basic')
                self.end_headers()
                self.wfile.write(b"denied") #TODO remove
        elif self.path.startswith('/check-card-and-code'):
            query_components = parse_qs(urlparse(self.path).query)
            code = query_components['code'][0]
            card = query_components['card'][0]
            device_id = query_components['id'][0]
        
            # check = self.check_code(code, device_id)
            # if check:
            check = self.check_card_and_code(code, card, device_id)
            if check:
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"ok") #TODO remove
            else:
                self.send_response(401)
                self.send_header('WWW-authenticate', 'Basic')
                self.end_headers()
                self.wfile.write(b"denied") #TODO remove
            # else:
            #     self.send_response(401)
            #     self.send_header('WWW-authenticate', 'Basic')
            #     self.end_headers()
            #     self.wfile.write(b"denied") #TODO remove

                
                
    def add_log(self, device, access, element, individual = False):
        message = f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] | device: {device:>10} | {access} | {element}\n'
        if individual:
            message = message[:-1] + f" | individual: {individual}\n"
        with open("./db/logs.txt", 'a') as file:
            file.write(message)
    
     
    def check_code(self, code_to_check: str,  device_id: str) -> bool:
        with open("./db/people.db", "rb") as file:
            data = load(file)
        if len(code_to_check)==4:
            for name, code, card, access_lvl in data:
                if code_to_check == code:
                    with open("./db/devices.db", "rb") as file:
                        devices_data = load(file)
                    device_access_lvl, device_people = devices_data[device_id]
                    if access_lvl >= device_access_lvl:
                        self.add_log(device_id, "ACCESS GRANTED", 'code', name)
                        return True
                    # elif name in device_people:
                    #     self.add_log(device_id, "ACCESS GRANTED", 'code', name)
                    #     return True
                    else:
                        self.add_log(device_id, "ACCESS DENIED ", 'code', name)
                        return False
            self.add_log(device_id, "ACCESS DENIED ", 'code', "unknown")
            return False
        else:
            for name, code, card, access_lvl in data:
                if code_to_check == card:
                    with open("./db/devices.db", "rb") as file:
                        devices_data = load(file)
                    device_access_lvl, device_people = devices_data[device_id]
                    if access_lvl >= device_access_lvl:
                        self.add_log(device_id, "ACCESS GRANTED", 'card', name)
                        return True
                    # elif name in device_people:
                    #     self.add_log(device_id, "ACCESS GRANTED", 'card', name)
                    #     return True
                    else:
                        self.add_log(device_id, "ACCESS DENIED ", 'card', name)
                        return False
            with open('./db/cards.db','rb') as file:
                cards = []
                while True:
                    try:
                        cards.append(load(file))
                    except EOFError:
                        break
            if code_to_check not in cards:
                with open('./db/cards.db','ab') as file:
                    dump(code_to_check,file)
                self.add_log(device_id, "ADDED NEW CARD", 'new card')
            else: 
                self.add_log(device_id, "OWNERLESS CARD", 'ownerless card')
            return False
                    
                    
    def check_card_and_code(self, code_to_check: str, card_to_check: str,  device_id: str) -> bool:
        with open("./db/people.db", "rb") as file:
            data = load(file)
        # if len(code_to_check)==4:
        for name, code, card, access_lvl in data:
            if code_to_check == code and card_to_check == card:
                with open("./db/devices.db", "rb") as file:
                    devices_data = load(file)
                device_access_lvl, device_people = devices_data[device_id]
                if access_lvl >= device_access_lvl:
                    self.add_log(device_id, "ACCESS GRANTED", 'c&&c', name)
                    return True
                elif name in device_people:
                    self.add_log(device_id, "ACCESS GRANTED", 'c&&c', name)
                    return True
                else:
                    self.add_log(device_id, "ACCESS DENIED ", 'c&&c', name)
                    return False
                    
        self.add_log(device_id, "ACCESS DENIED ", 'c&&c', "unknown")
        return False
            

if __name__ == "__main__":
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()
