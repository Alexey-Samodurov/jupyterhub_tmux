import click
from app.tmux_creator import NotebookTmuxCreator


def stop_all():
    NotebookTmuxCreator().kill_all_tmux()


if __name__ == '__main__':
    stop_all()
