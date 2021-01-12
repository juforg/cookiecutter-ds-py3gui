# !/usr/bin/env python
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#      SJ编程规范
# 命名：
#    1. 见名思意，变量的名字必须准确反映它的含义和内容
#    2. 遵循当前语言的变量命名规则
#    3. 不要对不同使用目的的变量使用同一个变量名
#    4. 同个项目不要使用不同名称表述同个东西
#    5. 函数/方法 使用动词+名词组合，其它使用名词组合
# 设计原则：
#    1. KISS原则： Keep it simple and stupid !
#    2. SOLID原则： S: 单一职责 O: 开闭原则 L: 迪米特法则 I: 接口隔离原则 D: 依赖倒置原则
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# main module executed when run command
# python -m {{cookiecutter.repo_name}}_gui_main

# This is the main application module ........................................

# standard modules
import os, sys
import datetime
import gettext
from threading import Thread
import time

# install update if user downloaded an update batch "FROZEN application only"
if hasattr(sys, 'frozen'):  # like if application frozen by cx_freeze
    current_directory = os.path.dirname(sys.executable)

    # Should copy contents of {{cookiecutter.repo_name}}_update_files folder and overwrite {{cookiecutter.repo_name}} original files
    update_batch_path = os.path.join(current_directory, '{{cookiecutter.repo_name}}_update_files')
    if os.path.isdir(update_batch_path):
        from distutils.dir_util import copy_tree, remove_tree
        copy_tree(update_batch_path, current_directory)
        print('done installing updates')

        # delete folder
        remove_tree(update_batch_path)


# All translations provided for illustrative purposes only.
# lo = gettext.translation('messages', localedir='gui/locale', languages=['de'])
# lo = gettext.translation('messages', localedir='gui/locale', languages=['es'])
# lo.install()

# install update if user downloaded an update batch "FROZEN application only"
if hasattr(sys, 'frozen'):  # like if application frozen by cx_freeze
    current_directory = os.path.dirname(sys.executable)

    # Should copy contents of dstk_update_files folder and overwrite dstk original files
    update_batch_path = os.path.join(current_directory, '{{cookiecutter.repo_name}}_update_files')
    if os.path.isdir(update_batch_path):
        from distutils.dir_util import copy_tree, remove_tree

        copy_tree(update_batch_path, current_directory)
        print('done installing updates')

        # delete folder
        remove_tree(update_batch_path)

# This code should stay on top to handle relative imports in case of direct call of pyIDM.py
if __package__ is None:
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(path))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

    __package__ = '{{cookiecutter.repo_name}}'
    import {{cookiecutter.repo_name}}

# local modules
from {{cookiecutter.repo_name}}.gui.utils import *
from {{cookiecutter.repo_name}}.gui import config
from {{cookiecutter.repo_name}}.gui.component import MainWindow, SysTray, sg

def is_solo():
    """to check if a previous app instance already running"""
    return True


def main():

    # quit if there is previous instance of this App. already running
    if not is_solo():
        print('previous instance already running')
        sg.Popup(f'{{cookiecutter.repo_name}} version {config.APP_VERSION} already running or maybe systray icon is active', title=f'{{cookiecutter.repo_name}} version {config.APP_VERSION}')
        config.shutdown = True
        return

    # run systray
    systray = SysTray()
    # Thread(target=systray.run, daemon=True).start()

    # create main window
    main_window = MainWindow()
    # Thread(target=main_window.run(), daemon=True).start()

    # create main run loop
    while True:

        if main_window and main_window.active:
            main_window.run()
            sleep_time = 0.01
        else:
            main_window = None
            sleep_time = 0.5

        # sleep a little to save cpu resources
        time.sleep(sleep_time)

        if systray.active:
            # set hover text for systray
            state = f'{{cookiecutter.repo_name}} is active \n{main_window.total_speed}' if not config.terminate else '{{cookiecutter.repo_name}} is off'
            systray.update(hover_text=state)

        # read Main queue
        for _ in range(config.main_q.qsize()):
            value = config.main_q.get()
            if value == 'start_main_window':
                if not main_window:
                    main_window = MainWindow()
                else:
                    main_window.un_hide()
            elif value == 'minimize_to_systray':
                if main_window:
                    main_window.hide()
            elif value == 'close_to_systray':
                if main_window:
                    main_window.close()

        # global shutdown flag
        if config.shutdown or not(main_window or systray.active):
            # print('config.shutdown, systray.active', config.shutdown, systray.active)
            systray.shutdown()
            config.shutdown = True
            if main_window:
                main_window.close()
            break


if __name__ == '__main__':
    main()

