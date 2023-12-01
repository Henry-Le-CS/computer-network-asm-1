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
                
    elif keyword.lower() == 'exit':
        method = 'shutdown'

    else:
        raise MyException('Invalid command !')
    
    return method, payload