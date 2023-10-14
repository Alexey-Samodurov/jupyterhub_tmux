import logging
import socket
import subprocess
from pathlib import Path
from uuid import uuid4

from libtmux import Server
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("notebook_tmux_creator_debug.log"),
        logging.StreamHandler()
    ]
)


class NotebookTmuxCreator:
    """
    Class for create tmux sessions with jupyter notebooks. It's create temporary dirs for notebooks,
    create tmux sessions, install dependencies and start jupyter notebook in tmux session.
    All files will be deleted after stop tmux session.

    :param num_sessions: number of sessions to create, by default 0
    :param default_port: default port for jupyter notebook, by default 2000
    """

    def __init__(self, num_sessions: int = 0, default_port: int = 2000):
        self.num_sessions = num_sessions
        self._default_port = default_port
        assert isinstance(self.num_sessions, int), 'Number of sessions must be integer!'

    @property
    def get_tmux_server(self) -> Server:
        """Get tmux server"""
        return Server()

    @property
    def get_resolve_host(self) -> str:
        """Get resolve host, in this case it's localhost"""
        return 'localhost'

    @property
    def get_random_token(self) -> uuid4:
        """Get random token for jupyter notebook"""
        return uuid4()

    def check_port(self, port) -> bool:
        """Check port for availability"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((self.get_resolve_host, port)) == 0

    def start_tmux_session(self, session_numb) -> Server.new_session:
        """Start new tmux session"""
        return self.get_tmux_server.new_session(session_name=[session_numb])

    def get_tmux_sessions(self) -> Server.list_sessions:
        """Get all tmux sessions"""
        return self.get_tmux_server.sessions

    def kill_target_session(self, session_numb):
        """
        Kill target tmux session

        :param session_numb: number of session
        """
        self.get_tmux_server.kill_session(target_session=[session_numb])
        self.drop_notebooks_dir(session_numb)

    def kill_all_tmux(self):
        """Find all tmux sessions and kill them"""
        for num in [int(x.name.replace(']', '').replace('[', ''))
                    for x in self.get_tmux_sessions()]:
            self.drop_notebooks_dir(num)
        self.get_tmux_server.kill_server()

    def create_notebooks_dirs(self):
        """Create temporary dirs for notebooks"""
        for num in tqdm(range(self.num_sessions), f'Create notebooks dirs'):
            Path('tmp', f'dir{num}').mkdir(parents=True, exist_ok=True)

    @staticmethod
    def drop_notebooks_dir(session_numb):
        """
        Drop temporary dir for notebooks

        :param session_numb: number of session
        """
        path = Path('tmp', f'dir{session_numb}')
        logging.info(f'Drop temporary dir: {path}')
        subprocess.run(["rm", "-rf", str(path)])

    @staticmethod
    def install_notebooks_venv(session_numb):
        """
        Install dependencies and create virtual environment for notebooks

        :param session_numb: number of session
        """
        subprocess.run(['pip3', '-q', 'install', '--user', 'ipykernel'])
        subprocess.run(['python3', '-m', 'venv', f'./tmp/dir{session_numb}/.venv{session_numb}'])
        subprocess.run(['source', f'./tmp/dir{session_numb}/.venv{session_numb}/bin/activate'], shell=True)
        subprocess.run(['pip3', 'install', '-qr', './requirements.txt'])
        subprocess.run(['python3', '-m', 'ipykernel', 'install', '--user', f'--name=.venv{session_numb}'])

    def start_notebooks(self):
        """Start notebooks in tmux sessions"""
        port = self._default_port
        self.create_notebooks_dirs()
        for num in tqdm(range(self.num_sessions), desc='Install dependencies, start new session'):
            if not self.check_port(port=port):
                logging.warning(f'Port {port} in use trying next: {port + 1}')
                port += 1
            token = self.get_random_token
            window = self.start_tmux_session(session_numb=num).new_window(window_name=num)
            self.install_notebooks_venv(session_numb=num)
            window.attached_pane.send_keys(
                f"""
                jupyter notebook --ip {self.get_resolve_host} \
                --port {port} \
                --no-browser \
                --NotebookApp.token={token} \
                --NotebookApp.notebook_dir=./tmp/dir{num}
                """)

            logging.info(f'Start notebook on http://{self.get_resolve_host}:{port} token: {token} session name: {num}')
            self._default_port += 1


if __name__ == '__main__':
    tmux = NotebookTmuxCreator(1)
    # tmux.start_notebooks()
    # tmux.kill_target_session(0)
    # tmux.kill_all_tmux()
    print([x.name for x in tmux.get_tmux_sessions()])
    tmux.kill_all_tmux()
