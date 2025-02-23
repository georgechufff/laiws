import re
import os

def read_file(filename: str) -> str:
    with open(filename, 'r', encoding='utf-8') as file:
        content = ''.join(file.readlines())
    return re.sub(' +', ' ', re.sub('\s', ' ', content)).lstrip().rstrip()

path = __file__.replace('__init__.py', '')
TRANSLATION_PROMPT = read_file(os.path.join(path, 'translation_prompt')).format(lang='Russian')
INTRODUCTION_PROMPT = read_file(os.path.join(path, 'introduction_prompt'))