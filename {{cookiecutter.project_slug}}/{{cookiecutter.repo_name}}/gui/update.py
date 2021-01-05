"""
    pyIDM

    multi-connections internet download manager, based on "pyCuRL/curl", "youtube_dl", and "PySimpleGUI"

    :copyright: (c) 2019-2020 by Mahmoud Elshahat.
    :license: GNU LGPLv3, see LICENSE for more details.
"""

# check and update application
import hashlib
import json
import py_compile
import shutil
import sys
import zipfile
import queue
import time
from threading import Thread
from distutils.dir_util import copy_tree

from . import config
import os

from .utils import log, run_command, delete_folder, version_value, delete_file
import webbrowser


def check_for_update():
    """download version.py from github, extract latest version number return app latest version"
    """

    # do not use, will use get_changelog() instead

    source_code_url = 'https://github.com/pyIDM/pyIDM/blob/master/pyidm/version.py'
    new_release_url = 'https://github.com/pyIDM/pyIDM/releases/download/extra/version.py'
    url = new_release_url if config.FROZEN else source_code_url

    # get BytesIO object
    buffer = download(url)

    if buffer:
        # convert to string
        contents = buffer.getvalue().decode()

        # extract version number from contents
        latest_version = contents.rsplit(maxsplit=1)[-1].replace("'", '')

        return latest_version

    else:
        log("check_for_update() --> couldn't check for update, url is unreachable")
        return None


def get_changelog():
    """download ChangeLog.txt from github, extract latest version number, return a tuple of (latest_version, contents)
    """

    # url will be chosen depend on frozen state of the application
    source_code_url = 'https://github.com/pyIDM/pyIDM/raw/master/ChangeLog.txt'
    new_release_url = 'https://github.com/pyIDM/pyIDM/releases/download/extra/ChangeLog.txt'
    url = new_release_url if config.FROZEN else source_code_url

    # url = new_release_url

    # get BytesIO object
    log('check for PyIDM latest version ...')
    buffer = download(url, verbose=False)

    if buffer:
        # convert to string
        contents = buffer.getvalue().decode()

        # extract version number from contents
        latest_version = contents.splitlines()[0].replace(':', '').strip()

        return latest_version, contents
    else:
        log("check_for_update() --> couldn't check for update, url is unreachable")
        return None


def update():
    if config.FROZEN:
        try:
            done = download_update_batch()
            if not done:
                log('Update Failed, check log for more info', showpopup=True)
                return False

            # try to install update batch
            done = install_update_batch()
            if not done:
                log("Couldn't install updates while application running, please restart PyIDM\n\n",
                    'IMPORTANT: when you restart PyIDM it might take around 30 seconds installing updates\n',
                    'before it loads completely\n '
                    'If you see error message just ignore it and start the application again\n', showpopup=True)
                return False
            else:
                log('Update finished successfully, Please restart PyIDM', showpopup=True)
                return True
        except Exception as e:
            log('update()> error', e)
    else:
        open_update_link()


def open_update_link():
    url = config.LATEST_RELEASE_URL if config.FROZEN else config.APP_URL
    webbrowser.open_new(url)


def get_update_batch_info() -> dict:
    """
    download updateinfo.json file to get update batch's info, parse info and return a dict
    :return: dict of parsed info
    """
    # example contents of updateinfo.json
    # {
    #     "url": "https://github.com/pyIDM/PyIDM/releases/download/2020.5.4/2020.5.4_update_batch_1.zip",
    #     "minimum_version": "2020.5.4",
    #     "max_version": "2020.5.4",
    #     "sha256": "4BE94A30CCB7B990FAFF8EDCEDB29E16D45E43412FF5006FD936A62E6B2EA8E2"
    # }

    # todo: this file should be with github source code
    url = 'https://github.com/pyIDM/pyIDM/releases/download/extra/testupdateinfo.json'

    # get latest update batch url
    log('check for update batches')
    buffer = download(url, verbose=False)
    if buffer:
        log('decode buffer')
        buffer = buffer.getvalue().decode()  # convert to string
        log('read json information')
        try:
            info = json.loads(buffer)
            return info
        except:
            log('get_update_batch_info().json, Failed to read info from downloaded file')

    return {}


def download_update_batch():
    """for frozen windows app, will download only the updated files from server"""

    info = get_update_batch_info()

    if info:
        url = info.get('url')
        minimum_version = info.get('minimum_version')
        max_version = info.get('max_version')
        sha256_hash = info.get('sha256')

        if version_value(config.APP_VERSION) < version_value(minimum_version):
            log('Minimum version allowed to receive this update is:', minimum_version, '\n',
                'Please download the full version instead')
            return False
        elif version_value(config.APP_VERSION) > version_value(max_version):
            log('Max. version allowed to receive this update is:', max_version, '\n',
                'Your version already has this batch')
            return False

        log('downloading "update files", please wait...')
        target_path = os.path.join(config.current_directory, 'PyIDM_update_files.zip')
        buffer = download(url, file_name=target_path)

        if not buffer:
            log('downloading "update files", Failed!!!')
            return False

        # check download integrity / hash
        log('Integrity check ....')
        download_hash = hashlib.sha256(buffer.read()).hexdigest()

        # close buffer
        buffer.close()

        if download_hash.lower() != sha256_hash.lower():
            log('Integrity check failed, update batch has different hash, quitting...')
            log('download_hash, original_hash:')
            log('\n', download_hash, '\n', sha256_hash)
            return False

        # unzipping downloaded file
        log('unzipping downloaded file')
        with zipfile.ZipFile(target_path, 'r') as zip_ref:  # extract zip file
            zip_ref.extractall(config.current_directory)

        log('delete zip file')
        delete_file(target_path, verbose=True)

        # write hash to update_batches_record file "append"
        log('write update batch hash to update_batches_record')
        with open(config.update_batches_record, 'a') as file:
            file.write('\n')
            file.write(sha256_hash)

        return True


def install_update_batch():
    try:
        log('overwrite old PyIDM files')
        update_batch_path = os.path.join(config.current_directory, 'PyIDM_update_files')
        copy_tree(update_batch_path, config.current_directory)

        log('delete temp files')
        delete_folder(update_batch_path)
        return True
    except Exception as e:
        log('install_update_batch()> error', e)
        return False


def check_for_ytdl_update():
    """it will download "version.py" file from github to check for a new version, return ytdl_latest_version
    """

    url = 'https://github.com/ytdl-org/youtube-dl/raw/master/youtube_dl/version.py'

    # get BytesIO object
    log('check for youtube-dl latest version on Github...')
    buffer = download(url, verbose=False)

    if buffer:
        # convert to string
        contents = buffer.getvalue().decode()

        # extract version number from contents
        latest_version = contents.rsplit(maxsplit=1)[-1].replace("'", '')

        return latest_version

    else:
        log("check_for_update() --> couldn't check for update, url is unreachable")
        return None


def update_youtube_dl():
    """This block for updating youtube-dl module in the freezed application folder in windows"""
    current_directory = config.current_directory

    # check if the application runs from a windows cx_freeze executable
    # if run from source code, we will update system installed package and exit
    if not config.FROZEN:
        cmd = f'"{sys.executable}" -m pip install youtube_dl --upgrade'
        success, output = run_command(cmd)
        if success:
            log('successfully updated youtube_dl')
        return

    # make temp folder
    log('making temp folder in:', current_directory)
    if 'temp' not in os.listdir(current_directory):
        os.mkdir(os.path.join(current_directory, 'temp'))

    # paths
    target_module = os.path.join(current_directory, 'lib/youtube_dl')
    bkup_module = os.path.join(current_directory, 'lib/youtube_dl_bkup')
    new_module = os.path.join(current_directory, 'temp/youtube-dl-master/youtube_dl')

    def bkup():
        # backup current youtube-dl module folder

        log('delete previous backup')
        delete_folder(bkup_module)

        log('backup current youtube-dl module')
        shutil.copytree(target_module, bkup_module)

    def unzip():
        # extract zipped module
        with zipfile.ZipFile('temp/youtube-dl.zip', 'r') as zip_ref:
            zip_ref.extractall(path=os.path.join(current_directory, 'temp'))

    def compile_file(q):
        while q.qsize():
            file = q.get()

            if file.endswith('.py'):
                try:
                    py_compile.compile(file, cfile=file + 'c')
                    os.remove(file)
                except Exception as e:
                    log('compile_file()> error', e)
            else:
                print(file, 'not .py file')

    def compile_all():
        q = queue.Queue()

        # get files list and add it to queue
        for item in os.listdir(new_module):
            item = os.path.join(new_module, item)

            if os.path.isfile(item):
                file = item
                # compile_file(file)
                q.put(file)
            else:
                folder = item
                for file in os.listdir(folder):
                    file = os.path.join(folder, file)
                    # compile_file(file)
                    q.put(file)

        tot_files_count = q.qsize()
        last_percent_value = 0

        # create 10 worker threads
        threads = []
        for _ in range(10):
            t = Thread(target=compile_file, args=(q,), daemon=True)
            threads.append(t)
            t.start()

        # watch threads until finished
        while True:
            live_threads = [t for t in threads if t.is_alive()]
            processed_files_count = tot_files_count - q.qsize()
            percent = processed_files_count * 100 // tot_files_count
            if percent != last_percent_value:
                last_percent_value = percent
                log('#', start='', end='' if percent < 100 else '\n')

            if not live_threads and not q.qsize():
                break

            time.sleep(0.1) 
        log('Finished compiling to .pyc files')

    def overwrite_module():
        delete_folder(target_module)
        shutil.move(new_module, target_module)
        log('new module copied to:', target_module)

    # start processing -------------------------------------------------------
    log('start updating youtube-dl please wait ...')

    try:
        # backup
        bkup()

        # download from github
        log('step 1 of 4: downloading youtube-dl raw files')
        url = 'https://github.com/ytdl-org/youtube-dl/archive/master.zip'
        response = download(url, 'temp/youtube-dl.zip')
        if response is False:
            log('failed to download youtube-dl, abort update')
            return

        # extract zip file
        log('step 2 of 4: extracting youtube-dl.zip')

        # use a thread to show some progress while unzipping
        t = Thread(target=unzip)
        t.start()
        while t.is_alive():
            log('#', start='', end='')
            time.sleep(0.5)

        log('\n', start='')
        log('youtube-dl.zip extracted to: ', current_directory + '/temp')

        # compile files from py to pyc
        log('step 3 of 4: compiling files, please wait')
        compile_all()

        # delete old youtube-dl module and replace it with new one
        log('step 4 of 4: overwrite old youtube-dl module')
        overwrite_module()

        # clean old files
        delete_folder('temp')
        log('delete temp folder')
        log('youtube_dl module ..... done updating')
        log('please restart Application now .................................')
    except Exception as e:
        log('update_youtube_dl()> error', e)


def rollback_ytdl_update():
    """rollback last youtube-dl update"""
    if not config.FROZEN:
        log('rollback youtube-dl update is currently working on portable windows version only')
        return

    log('rollback last youtube-dl update ................................')

    # paths
    current_directory = config.current_directory
    target_module = os.path.join(current_directory, 'lib/youtube_dl')
    bkup_module = os.path.join(current_directory, 'lib/youtube_dl_bkup')

    try:
        # find a backup first
        if os.path.isdir(bkup_module):
            log('delete active youtube-dl module')
            delete_folder(target_module)

            log('copy backup youtube-dl module')
            shutil.copytree(bkup_module, target_module)

            log('done restoring youtube-dl module')
            log('please restart Application now .................................')
        else:
            log('No backup youtube-dl modules found')

    except Exception as e:
        log('rollback_ytdl_update()> error', e)






