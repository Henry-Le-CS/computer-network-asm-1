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

    else:
        raise MyException('Invalid command !')
    
    return method, payload

def parse_client_request (request: str, address):
    splitted_command = request.splitlines()
    
    method = ''
    payload = None
    delimiter = '\n'
    
    request_method = splitted_command[0].strip()
    
    if request_method == 'SET_HOST_ADDRESSES':
        validate_length(request, 2, delimiter=delimiter) # keyword, client_name
        
        client_name = splitted_command[1]
        client_upload_port = splitted_command[2]
        
        payload = (client_name, address, client_upload_port)
        method = 'set_client_addresses'
        
    elif request_method == 'PUBLISH_FILE_INFO':
        validate_length(request, 4, delimiter=delimiter) # keyword, file_name, file_path, upload_port
        
        file_path = splitted_command[1]
        file_name = splitted_command[2]
        upload_port = splitted_command[3]
        
        address = (address[0], upload_port)
        
        payload = (file_name, file_path, address)
        method = 'publish_filename'
    
    elif request_method == 'FETCH_FILE_INFO':
        validate_length(request, 2, delimiter=delimiter) # keyword, file_name
        
        file_name = splitted_command[1]
        
        payload = (file_name, address)
        method = 'fetch_peers'
    
    elif request_method == 'FETCH_AVAILABLE_PEERS':
        payload = address
        method = 'fetch_available_peers'
    else:
        raise MyException('Invalid request.')

    return method, payload