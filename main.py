import utils as utils
import smtp_protocol

t_server = 'smtp.yandex.ru'
t_login, t_pass = 'JarlsFake@yandex.ru', 'soapsoap'
test = (t_server, t_login, t_pass)


def main(server, login, password):
    used_sock = smtp_protocol.request_with_ssl(server, 465, login)
    smtp_protocol.auth(used_sock, login, password)
    conf = get_conf('mail.conf')
    tokens = [
        conf.get('receiver'),
        conf.get('subject'),
        conf.get('text'),
        conf.get('path')
    ]
    message = utils.compile_message(login, *tokens)
    log_message(message)
    smtp_protocol.send_message(used_sock, login, tokens[0], message)
    smtp_protocol.kill(used_sock)



def get_conf(file_name):
    try:
        return utils.parse_config(file_name)
    except FileNotFoundError:
        print('Check conf file')

def log_message(mess):
    with open('message.txt', 'w') as f:
        f.write(mess)

if __name__ == '__main__':
    main(*test)
