import re
import socket
import ssl
from base64 import b64encode


def request_with_ssl(address, port, username):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock = ssl.wrap_socket(sock)
    sock.settimeout(1)
    sock.connect((address, port))
    sock.recv(4096)

    sock.send(bytes(f'EHLO {username}\n', 'UTF-8'))
    message = sock.recv(4096)
    code = extract_code(message)
    if code != 250:
        raise ConnectionError(f'EHLO try failed with code {code}')
    else:
        print('EHLO accepted')
    return sock


def auth(sock, username, password):
    sep = b'\n'
    dialogue = [
        (b'AUTH LOGIN' + sep, 334),
        (b64encode(username.encode('utf-8')) + sep, 334),
        (b64encode(password.encode('utf-8')) + sep, 235)
        ]
    have_nice_conversation(sock, 'Auth', dialogue)
    print('Successfully authorized!')

code_regex = re.compile('(\d{3})')
def extract_code(mess_bytes):
    mess_str = mess_bytes.decode('utf-8')
    match = code_regex.search(mess_str)
    return int(match.group()) if match.group() else -1

def have_nice_conversation(sock, conversation_name, dialogue):
    for i in range(len(dialogue)):
        query, answer_code = dialogue[i]
        sock.send(query)
        code = extract_code(sock.recv(4096))
        if code != answer_code:
            raise ConnectionError(f'{conversation_name} sadly ruined on {i} step with code {code}!')

def send_message(sock, sender, receiver, message):
    s = sender.encode('utf-8')
    r = receiver.encode('utf-8')
    sep = b'\n'
    dialogue = [
        (b'mail from: ' + s + sep, 250),
        (b'rcpt to: ' + r + sep, 250),
        (b'data' + sep, 354)
    ]
    have_nice_conversation(sock, 'Sending message', dialogue)
    sock.send(message.encode('utf-8') + sep)
    sock.send(b'.' + sep)


def kill(sock):
    sock.send(b'QUIT\n')
    sock.close()
