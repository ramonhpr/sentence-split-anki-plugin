from os.path import join, dirname, abspath, exists
from threading import Thread
import subprocess


class VenvRunner(Thread):
    venv_name = 'venv'

    def setup(self):
        if not exists(join(self.directory, self.venv_name)):
            subprocess.Popen(f'python3 -m venv {join(self.directory, self.venv_name)}'.split()).communicate()
            subprocess.Popen(f'{self.pip_path} install -r {join(self.directory, "requirements.txt")}'.split()).communicate()
            subprocess.Popen(f'{self.pip_path} install -e {self.directory}'.split()).communicate()

    def run_python_command(self, command=''):
        out, _ = subprocess.Popen(f'{self.python_path} -c'.split() + [command], stdout=subprocess.PIPE).communicate()
        return eval(out)  # FIXME: possible command injection

    def run_main(self, from_lang, to_lang, phrase) -> str:
        if '\n' not in phrase:
            out, _ = subprocess.Popen(f'{self.python_path} {join(self.directory, "main.py")} {from_lang} {to_lang} \"{phrase}\"'.split(), stdout=subprocess.PIPE).communicate()
            return out.decode('utf-8')
        else:
            out = ''
            for i in phrase.split('\n'):
                out += self.run_main(from_lang, to_lang, i)
            return out

    def __init__(self):
        self.directory = join(dirname(abspath(__file__)), '..')
        self.pip_path = join(self.directory, self.venv_name, 'bin', 'pip')
        self.python_path = join(self.directory, self.venv_name, 'bin', 'python3')
        self.setup()
        super(VenvRunner, self).__init__(target=self.run_python_command, name='VenvRunner', daemon=True)

    def start(self) -> None:
        super(VenvRunner, self).start()
