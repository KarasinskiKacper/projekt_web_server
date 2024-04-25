name ='a'
device_personal_access = ['a','b']
x=f'<input type="checkbox" id="personal-access-{name}" name="personal-access-{name}" value="{name}" {"checked" if name in device_personal_access else ''} ><label for="personal-access-{name}">name</label><br>'
                
print(x)