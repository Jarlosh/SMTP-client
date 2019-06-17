import os
import sys
import uuid

from base64 import b64encode

def bytes_to_b64(source_bytes):
    return b64encode(source_bytes).decode('utf-8')

def b64(source_text):
    return b64encode(source_text.encode('utf-8')).decode('utf-8')


def get_binary_from(directory):
    for filename in os.listdir(sys.path[0] + directory):
        with open(os.path.join(sys.path[0] + directory, filename), 'rb') as file:
            content = b''
            for lines in file:
                content += lines
            yield (filename, bytes_to_b64(content))


def make_boundary(text):
    boundary = ''
    while boundary == '' or text.find(boundary):
        boundary = str(uuid.uuid4())
    return boundary


def compile_message(sender, receiver, subject, text, directory):
    e_subject = f'=?UTF-8?B?{b64(subject)}?='
    e_text = b64(text)
    boundary = make_boundary(text)

    body_header = '\n'.join([
        'Mime-Version: 1.0',
        f'Content-Type: multipart/mixed; boundary="{boundary}"',
        '',
        f'--{boundary}',
        'Content-Type: text/plain;',
        '\tcharset=\"UTF-8\"',
        'Content-Transfer-Encoding: base64',
        '',
        e_text,
    ])
    parts = []
    for binary in get_binary_from(directory):
        part = '\n'.join([
            '--{0}',
            'Content-Type: application/octet-stream; name={1}',
            'Content-Transfer-Encoding: base64',
            'Content-Disposition: inline; filename={1}',
            '',
            '{2}',
            ''
        ]).format(boundary, *binary)
        parts.append(part)
    finisher = [f'--{boundary}--\n']
    body = '\n'.join([body_header] + parts + finisher)

    message = '\n'.join([
        f'From:{sender}',
        f'To:{receiver}',
        f'Subject:{e_subject}',

        f'{body}',
        f'.'
    ])
    return message


def parse_config(file_name):
    res = {}
    with open(file_name, 'r') as file_name:
        source = file_name.read().split('\n')
        res['receiver'] = source[0].split()[1]
        res['subject'] = source[1].split()[1]
        res['text'] = ' '.join(source[2].split()[1:])
        res['path'] = source[3].split()[1]
    return res
