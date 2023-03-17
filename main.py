import os
from datetime import datetime
import PySimpleGUI as sg
import shutil
from mega import Mega

def start_upload(window,credentials,folder):
    paths = window["-paths-"].get().split('\n')
    with open('setup.txt', 'w') as f:
        f.write(window['-paths-'].get())

    now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    shutil.rmtree('buffer')
    if not os.path.exists('buffer'): os.makedirs('buffer')
    for path in paths:
        if not os.path.exists(path):
            window['-display-'].update(f'path {path} not existing try again')
            return
        shutil.copytree(path, f'buffer/{path}')
        window['-display-'].update('copying')
        window.refresh()
    shutil.make_archive(f'savesbackup{now}', 'zip', 'buffer', verbose=True)
    window['-display-'].update('archive created')
    window.refresh()
    mega = Mega()
    session = mega.login(credentials[0], credentials[1])
    window['-display-'].update('login success')
    window.refresh()

    folder = session.find(folder)
    if folder is None:
        window['-display-'].update(f'upload folder not found in mega,uploading NOT succeful')
        window.refresh()
    else:
        window['-display-'].update('uploading')
        window.refresh()
        session.upload(f'savesbackup{now}.zip', folder[0])
        window['-display-'].update('done')
        window.refresh()


def main():
    paths = open('setup.txt', 'r').read()
    credentials = open('credentials.txt', 'r').read().split('\n')
    folder=credentials[2]
    layout = [
        [sg.Multiline(key="-paths-",size=(50,20),font=('Helvetica',13),default_text=paths),sg.VSeparator(),sg.Button('backup'),sg.Button('change credentials')],
        [sg.Text('email address'),sg.Multiline(key='-user-',default_text=credentials[0])],
        [sg.Text('password'), sg.Multiline(key='-pass-', default_text=credentials[1])],
        [sg.Text('folder to upload to'), sg.Multiline(key='-folder-', default_text=credentials[2])],
        [sg.Text('done', key='-display-')]

    ]
    window = sg.Window("Mega upload", layout)
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        if event =="change credentials":
            user=window["-user-"].get()
            password=window["-pass-"].get()
            folder=window["-folder-"].get()
            credentials=[user,password]
            with open('credentials.txt','w') as f:
                f.write(f'{user}\n{password}\n{folder}')
            window['-display-'].update('credentials changed')
            window.refresh()

        if event == "backup":
            start_upload(window,credentials,folder)


    window.close()
if __name__ == "__main__":
    main()
