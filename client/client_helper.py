import socket

class MyException(Exception):
    pass

def validate_length (text: str, length: int, delimiter: str = ' '):
    splitted_text = text.split(delimiter)
    
    if len(splitted_text) < length:
        raise MyException('Missing arguments')

def parse_client_cmd (command: str):
    """
    Args:
        command (str): User's command line

    Returns:
        method: Client's method
        payload: payload for corresponding method
    """
    
    splitted_command = command.split()
    
    method = ''
    payload = None
    
    keyword = splitted_command[0].strip()

    if keyword.lower() == 'publish':
        validate_length(command, 3)
        
        file_path, file_name = splitted_command[1], splitted_command[2]
        
        # Replace backslash with slash, so we can make new folder if they do not exists
        file_path = file_path.replace('\\', '/')
        
        payload = (file_path, file_name)
        method = 'publish_file_info'
    
    elif keyword.lower() == 'fetch':
        validate_length(command, 2) # keyword, file_name
        
        file_name = splitted_command[1]
        
        payload = file_name
        method = 'fetch_file_info'
        
    elif keyword.lower() == 'exit':
        method = 'shutdown'

    else:
        raise MyException('Invalid command !')
    
    return method, payload

def parse_server_request (request: str, address):
    splitted_command = request.splitlines()
    
    method = ''
    payload = None
    delimiter = '\n'
    
    keyword = splitted_command[0].strip()

    if keyword.lower() == 'ping':
        validate_length(request, 2)
        
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

    else:
        raise MyException('Invalid command !')
    
    return method, payload

def parse_server_response(response: str):
    splitted_res = response.splitlines()
    
    method = ''
    payload = None
    delimiter = '\n'
    
    keyword = splitted_res[0].strip()

    if keyword.lower() == 'peers':
        
        file_name = splitted_res[1]
        
        optionCount = len(splitted_res) # minus keyword, file_name line
        
        options = []
        
        for i in range(2, optionCount):
            current_option = splitted_res[i]
            
            hostname, host, port, file_path = current_option.split()
            options.append((hostname, host, port, file_path))
            
        payload = (file_name, options)
        method = 'select_peer'
    else:
        method = 'PRINT'
    return method, payload