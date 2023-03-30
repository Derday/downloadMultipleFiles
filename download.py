from time import sleep
from uldlib.downloader import Downloader
from uldlib.frontend import ConsoleFrontend
from uldlib.captcha import AutoReadCaptcha
from uldlib.torrunner import TorRunner
from pathlib import Path
import os
import shutil

class Download:

    def __init__(self) -> None:
        self.path = Path(os.path.dirname(__file__))
        self.tempFolder = self.path.joinpath('temp')
        self.index = 0
    
    def fromFile(self, file:str = 'input.txt') -> None:
        """
        Download files from urls, that are in `input file`
        """
        while True:
            line = self._nextLine(self.path.joinpath(file))
            if line:
                self.download(line, 50)
            else:
                break
    
    def _nextLine(self, path:Path) -> str:
        with open(path, 'r') as f:
            lines = f.readlines()
        self.index += 1
        try:
            if lines[self.index-1] == '\n':
                line = self._nextLine(path)
            line = lines[self.index-1].rstrip()
        except:
            line = None
        return line

    def download(self, url: str, parts: int = 25) -> None:
        """
        Downloads file from url
        """
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
            if file.endswith('.ucache') or file.endswith('*.udown'):
                os.remove(os.path.join(files, file))
            else:
                shutil.move(self.tempFolder.joinpath(file), out)



if __name__ == "__main__":
    downloader = Download()
    downloader.fromFile()
    downloader.cleanup()