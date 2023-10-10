import logging
import os
import socket
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

    def __init__(self, num_sessions: int = 0, default_port: int = 2000):
        self.num_sessions = num_sessions
        self._default_port = default_port
        assert isinstance(self.num_sessions, int), 'Number of sessions must be integer!'

    @property
    def get_tmux_server(self):
        return Server()

    @property
    def get_resolve_host(self):
        # hostname = socket.gethostname()
        # return socket.gethostbyname(hostname)
        return 'localhost'

    @property
    def get_random_token(self):
        return uuid4()

    def check_port(self, port) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((self.get_resolve_host, port)) == 0

    def start_tmux_session(self) -> Server.new_session:
        return self.get_tmux_server.new_session()

    def get_tmux_sessions(self):
        return self.get_tmux_server.sessions

    def kill_all_tmux(self):
        self.get_tmux_server.kill_server()

    def create_notebooks_dirs(self):
        for num in tqdm(range(self.num_sessions), f'Create notebooks dirs'):
            os.makedirs(f'dir{num}', exist_ok=True)

    def start_notebooks(self):
        port = self._default_port
        self.create_notebooks_dirs()
        for num in range(self.num_sessions):
            if not self.check_port(port=port):
                logging.warning(f'Port {port} in use trying next: {port + 1}')
                port += 1
            token = self.get_random_token
            window = self.start_tmux_session().new_window(window_name=num)
            window.attached_pane.send_keys(
                """python3 -m venv {dir}/.venv && source {dir}/.venv/bin/activate && pip3 install -r requirements.txt \
                && jupyter notebook --ip {} \
                --port {} \
                --no-browser \
                --NotebookApp.token={} \
                --NotebookApp.notebook_dir={dir}""".format(
                    self.get_resolve_host,
                    port,
                    token,
                    dir=f'./dir{num}'))
            logging.info(f'Start notebook on http://{self.get_resolve_host}:{port} token: {token}')
            self._default_port += 1


if __name__ == '__main__':
    tmux = NotebookTmuxCreator(10)
    # tmux.start_notebooks()
    # tmux.start_session()
    # tmux.start_session()
    print(tmux.get_tmux_sessions())
    tmux.kill_all_tmux()
    print(tmux.get_tmux_sessions())
