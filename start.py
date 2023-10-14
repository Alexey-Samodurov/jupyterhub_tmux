import click
from app.tmux_creator import NotebookTmuxCreator


@click.command()
@click.option('--sessions_num', help='Number of sessions to create', default=0, type=int)
def start(sessions_num: int):
    tmux = NotebookTmuxCreator(num_sessions=sessions_num)
    tmux.start_notebooks()


if __name__ == '__main__':
    start()