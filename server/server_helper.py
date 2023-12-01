import socket

class MyException(Exception):
    pass

def validate_length (text: str, length: int, delimiter: str = ' '):
    splitted_text = text.split(delimiter)
    
    if len(splitted_text) < length:
        raise MyException('Missing arguments')

def parse_server_cmd (command: str):
    """
    Args:
        command (str): User's command line

    Returns:
        method: Server's method
        payload: payload for corresponding method
    """
    
    splitted_command = command.split()
    
    method = ''
    payload = None
    
    keyword = splitted_command[0].strip()

    if keyword.lower() == 'ping':
        validate_length(command, 2)
        
        client_name = splitted_command[1]
        
        payload = client_name
        method = 'ping_client'
        
    elif keyword.lower() == 'discover':
        client_name = splitted_command[1]
        
        payload = client_name
        method = 'discover_client'

    elif keyword.lower() == 'list':
        method = 'list_client'
        
    elif keyword.lower() == 'exit':
        method = 'shutdown'

        print(payload)
    else:
        raise MyException('Invalid command !')
    
    return method, payload

def parse_client_request (request: str, address):
    splitted_command = request.split()
    
    method = ''
    payload = None
    
    keyword = splitted_command[0].strip()

    if keyword.lower() == 'set_client_name':
        validate_length(request, 2) # keyword, client_name
        
        client_name = splitted_command[1]
        
        payload = (client_name, address)
        method = 'set_client_name'
    else:
        raise MyException('Invalid request.')
    
    return method, payload