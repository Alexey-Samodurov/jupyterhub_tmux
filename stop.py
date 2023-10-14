import click
from app.tmux_creator import NotebookTmuxCreator


@click.command()
@click.option('--session_name', help='Number of session to stop', type=int)
def stop(session_name: int):
    tmux = NotebookTmuxCreator()
    tmux.kill_target_session(session_numb=session_name)


if __name__ == '__main__':
    stop()