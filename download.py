from uldlib.downloader import Downloader
from uldlib.frontend import ConsoleFrontend
from uldlib.captcha import AutoReadCaptcha
from pathlib import Path
import os
from os.path import isfile, join


PATH = Path(os.path.dirname(__file__))
TEMP_FOLDER = PATH.joinpath('temp')
OUT = PATH.joinpath('out')


def download(url, parts):
    frontend = ConsoleFrontend()
    model_path = TEMP_FOLDER.joinpath('model.tflite')
    model_download_url = 'https://github.com/JanPalasek/ulozto-captcha-breaker/releases/download/v2.2/model.tflite'
    solver = AutoReadCaptcha(model_path, model_download_url, frontend)
    d = Downloader(frontend, solver)
    timeout = 3
    d.download(url, parts, TEMP_FOLDER, timeout)
    d.terminate()


def cleanup():
    os.system(f'rm {TEMP_FOLDER.joinpath("*.ucache")}')
    os.system(f'rm {TEMP_FOLDER.joinpath("*.udown")}')
    files = [f for f in os.listdir(TEMP_FOLDER) if isfile(join(TEMP_FOLDER, f))]
    files.remove('model.tflite')
    for file in files:
        os.system(f'mv {TEMP_FOLDER}/"{file}" {OUT}')



with open('input.txt', 'r') as f:
    urls = f.readlines()

urls = list(map(lambda str: str.rstrip(), urls))
for url in urls:
    download(url, 50)


cleanup()





