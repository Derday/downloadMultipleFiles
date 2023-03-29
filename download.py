from uldlib.downloader import Downloader
from uldlib.frontend import ConsoleFrontend
from uldlib.captcha import AutoReadCaptcha
from pathlib import Path
import os
from os.path import isfile, join

class Download:

    def __init__(self) -> None:
        self.path = Path(os.path.dirname(__file__))
        self.tempFolder = self.path.joinpath('temp')
    
    def fromFile(self, file:str = 'input.txt') -> None:
        """
        Download files from urls, that are in `input file`
        """
        with open(self.path.joinpath(file), 'r') as f:
            urls = f.readlines()
        urls = list(map(lambda str: str.rstrip(), urls))
        for url in urls:
            self.download(url, 50)

    def download(self, url: str, parts: int) -> None:
        """
        Downloads file from url
        """
        frontend = ConsoleFrontend()
        model_path = self.tempFolder.joinpath('model.tflite')
        model_download_url = 'https://github.com/JanPalasek/ulozto-captcha-breaker/releases/download/v2.2/model.tflite'
        solver = AutoReadCaptcha(model_path, model_download_url, frontend)
        d = Downloader(frontend, solver)
        timeout = 3
        d.download(url, parts, self.tempFolder, timeout)
        d.terminate()

    def cleanup(self, outFolder: Path = None ) -> None:
        """
        Move downloaded files to different folder, removes the remaining `.ucache` and `.udown` files.
        """
        out = outFolder or self.path.joinpath('downloaded')
        os.system(f'rm {self.tempFolder.joinpath("*.ucache")}')
        os.system(f'rm {self.tempFolder.joinpath("*.udown")}')
        files = [f for f in os.listdir(self.tempFolder) if isfile(join(self.tempFolder, f))]
        files.remove('model.tflite')
        for file in files:
            os.system(f'mv {self.tempFolder}/"{file}" {out}')


if __name__ == "__main__":
    downloader = Download()
    downloader.fromFile()
    downloader.cleanup()