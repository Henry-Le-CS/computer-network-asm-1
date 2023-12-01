class MyException(Exception):
    pass

def validate_command_length (command: str, length: int):
    splitted_command = command.split()
    
    if len(splitted_command) < length:
        raise MyException('Missing arguments')

def switch_client_cmd (command: str):
    splitted_command = command.split()
    
    methods = ''
    payload = None
    
    keyword = splitted_command[0].strip()

    if keyword.lower() == 'ping':
        validate_command_length(command, 2)
        
        client_name = splitted_command[1]
        
        payload = client_name
        methods = 'ping_client'
        
    elif keyword.lower() == 'discover':
        client_name = splitted_command[1]
        
        payload = client_name
        methods = 'discover_client'

    elif keyword.lower() == 'list':
        methods = 'list_client'
        
    elif keyword.lower() == 'exit':
        methods = 'shutdown'
    else:
        print(keyword.lower())
        raise MyException('Invalid request.')
    
    return methods, payload