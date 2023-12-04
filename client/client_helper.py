import socket

class MyException(Exception):
    pass

def validate_length (text: str, length: int, delimiter: str = ' '):
    splitted_text = text.split(delimiter)
    
    if len(splitted_text) < length:
        raise MyException('Missing arguments')

def parse_client_cmd (command: str, is_selecting_peer: bool = False, peer_options: dict = {}):
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
        # validate_length(command, 3)
        file_path = None
        file_name = None
        
        # Allow current directory. eg ping test.txt
        if(len(splitted_command) < 3):
            file_path = "."
            file_name = splitted_command[1]
        else:
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

    elif is_selecting_peer:
        validate_length(command, 1)
        
        selected_peer = int(splitted_command[0])
        
        if(not peer_options[selected_peer]):
            raise MyException('Invalid peer !')
        
        splitted_payload = peer_options[selected_peer].split() # split a tring by space
          
        payload = tuple(splitted_payload)
        method = 'download_from_peer'
    else:
        raise MyException('Invalid command !')
    
    return method, payload

def parse_server_response(response: str):
    splitted_res = response.splitlines()
    
    method = ''
    payload = None
    
    keyword = splitted_res[0].strip()

    if keyword.lower() == 'peers':
        
        file_name = splitted_res[1]
        
        optionCount = len(splitted_res)
        
        options = []
        
        for i in range(2, optionCount):
            current_option = splitted_res[i]
            
            options.append(current_option)
            
        payload = (file_name, options)
        method = 'display_peer_options'
    else:
        method = 'print'
    return method, payload