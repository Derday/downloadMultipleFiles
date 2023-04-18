from bs4 import BeautifulSoup
from threading import Thread
from uldlib.downloader import Downloader
from uldlib.frontend import ConsoleFrontend
from uldlib.captcha import AutoReadCaptcha
from uldlib.torrunner import TorRunner
from pathlib import Path
import os
import shutil
import requests

class File:
    def __init__(self, url:str) -> None:
        self.url = url
        self.size: int
        self.length: str
        self.res: tuple(int, int)
        self.file_info(self.url)
    
    def file_info(self, url):
        ses = requests.get(url)
        source = ses.text
        soup = BeautifulSoup(source, 'html.parser')
        self.fileName = soup.title.string
        self.size = int(source.split('fileSize\': ')[1].split(',')[0])
        div = str(soup.find_all('div', {'class': 'info-media t-file-info-strip'})[0])
        if 'Čas' in str(div):
            self.length = div.split('Čas')[1][8:].split('</li>')[0]
            self.res = tuple(div.split('Rozlišení')[1][8:].split('</li>')[0].split('×'))
        else:
            self.length = None
            self.res = None

        # print(self.fileName)
        # print(self.size)
        # print(self.length)
        # print(self.res)

class Download:
    MB_PER_PART = 25
    def __init__(self) -> None:
        self.path = Path(os.path.dirname(__file__))
        self.tempFolder = self.path.joinpath('temp')
        self.queue = []
        self.run = False
        self.file: File
        
    def from_file(self, file:str = 'input.txt') -> None:
        """
        Download files from urls, that are in `input file`
        """
        self.index = 0
        while True:
            line = self._next_line(self.path.joinpath(file))
            if line:
                self.download(line, 50)
            else:
                break
    
    def _next_line(self, path:Path) -> str:
        with open(path, 'r') as f:
            lines = f.readlines()
        self.index += 1
        try:
            if lines[self.index-1] == '\n':
                line = self._next_line(path)
            line = lines[self.index-1].rstrip()
        except:
            line = None
        return line

    def add_to_queue(self, url: str, parts: int) -> None:
        self.queue.append({'url':url, 'parts':parts})
        if not self.run:
            t = Thread(target=self._paraler_download)
            t.start() 
    
    def _paraler_download(self) -> None:
        self.run = True
        url = self.queue[0]['url']
        parts = self.queue[0]['parts']
        while len(self.queue):
            self.download(url, parts)
            self.queue.pop(0)
        self.run = False

    def download(self, url: str, parts: int = None) -> None:
        """
        Downloads file from url
        """
        self.file = File(url)
        parts = parts or int(self.file.size/1000000/self.MB_PER_PART)
        frontend = ConsoleFrontend(show_parts=False)
        model_path = self.tempFolder.joinpath('model.tflite')
        model_download_url = 'https://github.com/JanPalasek/ulozto-captcha-breaker/releases/download/v2.2/model.tflite'
        solver = AutoReadCaptcha(model_path, model_download_url, frontend)
        tor = TorRunner(self.tempFolder, frontend.tor_log)
        d = Downloader(tor, frontend, solver)
        d.download(url=url, parts=parts, target_dir=self.tempFolder, temp_dir=self.tempFolder)
        d.terminate()
        
    def cleanup(self, outFolder: Path = None ) -> None:
        """
        Move downloaded files to different folder, removes the remaining `.ucache` and `.udown` files.
        """
        out = outFolder or self.path.joinpath('downloaded')
        if not out.exists():
            out.mkdir(parents = False, exist_ok = False)
        files = os.listdir(self.tempFolder)
        files.remove('model.tflite')
        for file in files:
            if file.endswith('.ucache') or file.endswith('.udown'):
                os.remove(self.tempFolder.joinpath(file))
            else:
                try:
                    shutil.move(self.tempFolder.joinpath(file), out)
                except Exception as e:
                    if str(e).endswith('already exists'):
                        os.rename(self.tempFolder.joinpath(file), self.tempFolder.joinpath(file.split('.')[0]+'_copy'+'.'+file.split('.')[-1]))
                        self.cleanup(out)


if __name__ == "__main__":
    downloader = Download()
    downloader.from_file()
    downloader.cleanup()