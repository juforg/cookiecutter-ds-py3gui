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
import gc
import webbrowser

import PySimpleGUI as sg
import tkinter.font
import os
import time
from threading import Thread

from .utils import *
from . import setting
from . import config
from . import update
from .iconsbase64 import *

# imports for systray icon
try:
    import pystray
    from PIL import Image
    import io
    import base64
except Exception as e:
    log('Warning!! "pystray" package is required for systray icon, import error', e, log_level=2)

# todo: this module needs some clean up
app_name = config.APP_NAME
# gui Settings
default_font = 'Helvetica 10'  # Helvetica font is guaranteed to work on all operating systems
config.all_themes = natural_sort(sg.ListOfLookAndFeelValues())
sg.SetOptions(icon=APP_ICON, font=default_font, auto_size_buttons=True, progress_meter_border_depth=0,
              border_width=1)

# transparent color for button which mimic current background, will be used as a parameter, ex. **transparent
transparent = {}


class MainWindow:
    def __init__(self):
        """This is the main application user interface window"""

        self.active = True  # active flag, if true this window will run in main application loop in "snp_mvp.py"


        # main window
        self.window = None

        # active child windows
        self.active_windows = []  # list holds active_Windows objects

        # url
        self.url = ''  # current url in url input widget
        self.url_timer = 0
        self.bad_headers = [0, range(400, 404), range(405, 418), range(500, 506)]  # response codes

        # update
        self.new_version_available = False
        self.new_version_description = None
        self.update_batch_available = False
        self.update_batch_description = None

        # thumbnail
        self.current_thumbnail = None

        # timers
        self.statusbar_timer = 0
        self.timer1 = 0
        self.timer2 = 0
        self.one_time = True
        self.check_for_update_timer = time.time() - 55  # run interval is 60 seconds, use 'time.time() - 55' to make first start after 5 seconds

        self.total_speed = ''

        # initial setup
        self.setup()

    @staticmethod
    def startup():
        # start log recorder
        Thread(target=log_recorder, daemon=True).start()

        log('-' * 50, config.APP_NAME, '-' * 50)
        log(f'Starting {config.APP_NAME} version:', config.APP_VERSION, 'Frozen' if config.FROZEN else 'Non-Frozen')
        log('operating system:', config.operating_system_info)

        log('current working directory:', config.current_directory)
        os.chdir(config.current_directory)

    def setup(self):
        """initial setup"""

        # empty main window's queue and log queue
        # for q in (config.main_window_q, config.log_q):
        #     reset_queue(q)

        # startup
        self.startup()

        # load stored setting from disk
        setting.load_setting()

        # set global theme
        self.change_theme()

        # override PySimpleGUI standard buttons' background with artwork using a decorator function
        def button_decorator(init_func):
            def new_init_func(self, *args, **kwargs):
                # pre processing arguments
                if not kwargs.get('font'):
                    button_text = kwargs.get('button_text') or args[0] or ' '
                    # adjust font to let text fit within button bg image boundaries
                    if len(button_text) < 6:
                        kwargs['font'] = 'any 10 bold'
                    else:
                        kwargs['font'] = 'any 9 bold'  # todo: measuring font will be more practical

                # calling Button __init__() constructor
                init_func(self, *args, **kwargs)

                # post process Button properties
                if not self.ImageData:
                    self.ImageData = default_button_icon
                    self.ButtonColor = ('black', sg.theme_background_color())
                    self.BorderWidth = 0

            return new_init_func

        # redefine Button constructor
        sg.Button.__init__ = button_decorator(sg.Button.__init__)

        # main window
        self.start_window()

        self.reset()

    def read_q(self):
        # read incoming messages from queue
        for _ in range(config.main_window_q.qsize()):
            if not self.active:
                return
            k, v = config.main_window_q.get()
            if k == 'url':
                self.window['url'](v.strip())
                self.on_url_text_change()

            elif k == 'popup':
                type_ = v['type_']
                if type_ == 'popup_no_buttons':
                    sg.popup_no_buttons(v['msg'], title=v['title'])
                else:
                    sg.popup(v['msg'], title=v['title'])

            elif k == 'show_update_gui':  # show update gui
                self.show_update_gui()

        # read commands coming from other threads / modules and execute them.
        for _ in range(config.commands_q.qsize()):
            try:
                command = ''
                command, args, kwargs = config.commands_q.get()
                log(f'MainWindow, received command: {command}(), args={args}, kwargs={kwargs}', log_level=3)
                getattr(self, command)(*args, **kwargs)
            except Exception as e:
                log('MainWindow, error running command:', command, e, log_level=3)

    # region gui design

    def create_main_tab(self):
        # get current bg and text colors
        bg_color = sg.theme_background_color()
        text_color = sg.theme_text_color() if sg.theme_text_color() != "1234567890" else 'black'

        layout = [
            # spacer
            [sg.T('', font='any 2')],

            # app icon and app name
            [sg.Image(data=APP_ICON, enable_events=True, key='app_icon'),
             sg.Text(f'{config.APP_NAME}', font='any 20', justification='center', key='app_name', enable_events=True),
             sg.T('New version available, click me for more info !', size=(50, 1), justification='center',
                  key='update_note', enable_events=True, font='any 9', visible=False),
             ],

            # url entry
            [sg.T('Link:  '),
            sg.Input("testintpu", enable_events=True, key='url', size=(49, 1),  right_click_menu=['url', ['copy url', 'paste url']]),
            sg.Button('', key='Retry', tooltip=' retry ', image_data=refresh_icon, **transparent)],

            # format id
            [sg.T(' ' * 300, key='format_id', font='any 9', pad=(5, 0))],

            # folder
            [sg.Image(data=folder_icon),
             sg.Input(config.download_folder, size=(55, 1), key='folder', enable_events=True, background_color=bg_color,
                      text_color=text_color, ),
             sg.B('', image_data=browse_icon, **transparent, key='browse',
                  button_type=sg.BUTTON_TYPE_BROWSE_FOLDER, target='folder')],

            # file name
            [sg.Text('File:', pad=(6, 0)),
             sg.Input('', size=(65, 1), key='name', enable_events=True, background_color=bg_color,
                      text_color=text_color), sg.Text('      ')],

            # file properties
            [sg.T('-' * 300, key='file_properties', font='any 9'),
             sg.T('', key='critical_settings_warning', visible=False, font='any 9', size=(30, 1))],

            # download button
            [sg.Column([[sg.B('', image_data=download_icon, key='Download', **transparent)]],
                       size=(166, 52), justification='center')],

        ]

        return layout

    def create_settings_tab(self):
        """settings tab with TabGroup"""

        proxy_tooltip = """proxy setting examples:
                - http://proxy_address:port
                - 157.245.224.29:3128

                or if authentication required: 
                - http://username:password@proxyserveraddress:port  

                then choose proxy type i.e. "http, https, socks4, or socks5"  
                """

        general = [
            [sg.T('', size=(60, 1)), sg.Button('About', key='about', pad=(5, 10))],

            [sg.T('Settings Folder:'),
             sg.Combo(values=['Local', 'Global'],
                      default_value='Local' if config.sett_folder == config.current_directory else 'Global',
                      key='sett_folder', enable_events=True),
             sg.T(config.sett_folder, key='sett_folder_text', size=(100, 1), font='any 9')],

            [sg.Text('Select Theme:  '),
             sg.Combo(values=config.all_themes, default_value=config.current_theme, size=(15, 1),
                      enable_events=True, key='themes'),
             sg.Text(f' Total: {len(config.all_themes)} Themes')],

            [sg.Checkbox('Monitor copied urls in clipboard', default=config.monitor_clipboard,
                         key='monitor', enable_events=True)],

            [sg.Checkbox("Show download window", key='show_download_window',
                         default=config.show_download_window, enable_events=True)],
            [sg.Checkbox("Auto close download window after finish downloading", key='auto_close_download_window',
                         default=config.auto_close_download_window, enable_events=True)],

            [sg.Checkbox("Show video Thumbnail", key='show_thumbnail', default=config.show_thumbnail,
                         enable_events=True)],

            [sg.Text('Segment size:  '), sg.Input(default_text=size_format(config.segment_size), size=(10, 1),
                                                  enable_events=True, key='segment_size'),
             sg.Text(f'Current value: {size_format(config.segment_size)}', size=(30, 1), key='seg_current_value'),
             sg.T('*ex: 512 KB or 5 MB', font='any 8')],

            [sg.Checkbox('Playlist: Fetch all videos info in advance - *not recommended!!* -', default=config.process_playlist,
                         enable_events=True, key='process_playlist')],

            [sg.Checkbox('Manually select audio format for dash videos', default=config.manually_select_dash_audio,
                         enable_events=True, key='manually_select_dash_audio')]
        ]

        network = [
            [sg.T('')],
            [sg.Checkbox('Speed Limit:', default=True if config.speed_limit else False,
                         key='speed_limit_switch', enable_events=True,
                         ),
             sg.Input(default_text=size_format(config.speed_limit) if config.speed_limit else '',
                      size=(10, 1), key='speed_limit',
                      disabled=False if config.speed_limit else True, enable_events=True),
             sg.T('0', size=(30, 1), key='current_speed_limit'),
             sg.T('*ex: 512 KB or 5 MB', font='any 8')],
            [sg.T('', font='any 1')],  # spacer
            [sg.Text('Max concurrent downloads:      '),
             sg.Combo(values=[x for x in range(1, 101)], size=(5, 1), enable_events=True,
                      key='max_concurrent_downloads', default_value=config.max_concurrent_downloads)],
            [sg.Text('Max connections per download:'),
             sg.Combo(values=[x for x in range(1, 101)], size=(5, 1), enable_events=True,
                      key='max_connections', default_value=config.max_connections)],
            [sg.T('', font='any 1')],  # spacer
            [sg.Checkbox('Proxy:', default=config.enable_proxy, key='enable_proxy',
                         enable_events=True),
             sg.I(default_text=config.raw_proxy, size=(25, 1), font='any 9', key='raw_proxy',
                  enable_events=True, disabled=not config.enable_proxy),
             sg.T('?', tooltip=proxy_tooltip, pad=(3, 1)),
             sg.Combo(['http', 'https', 'socks4', 'socks5'], default_value=config.proxy_type,
                      font='any 9',
                      enable_events=True, key='proxy_type'),
             sg.T(config.proxy if config.proxy else '_no proxy_', key='current_proxy_value',
                  size=(100, 1), font='any 9'),
             ],
            [sg.T('', font='any 1')],  # spacer

            [sg.Checkbox('Website Auth: ', default=config.use_web_auth, key='use_web_auth', enable_events=True),
             sg.T('    *user/pass will not be saved on disk', font='any 8')],
            [sg.T('        user: '),
             sg.I('', size=(25, 1), key='username', enable_events=True, disabled=not config.use_web_auth)],
            [sg.T('        Pass:'), sg.I('', size=(25, 1), key='password', enable_events=True,
                                         disabled=not config.use_web_auth, password_char='*')],
            [sg.T('', font='any 1')],  # spacer

            [sg.Checkbox('Referee url:   ', default=config.use_referer, key='use_referer', enable_events=True),
             sg.I(default_text=config.referer_url, size=(55, 1), font='any 9', key='referer_url',
                  enable_events=True, disabled=not config.use_referer)],

            [sg.Checkbox('Use Cookies:', default=config.use_cookies, key='use_cookies', enable_events=True),
             sg.I(default_text=config.cookie_file_path, size=(55, 1), font='any 9', key='cookie_file_path',
                  enable_events=True, disabled=not config.use_cookies), sg.FileBrowse('Browse')],


        ]

        systray = [
            [sg.T(' ', size=(100, 1))],
            [sg.T('SysTray:')],
            [sg.Frame(title='Action when closing Main Window:', layout=[
                [sg.T(' '), sg.Radio('Close App to systray', group_id='close_action', key='radio_close', enable_events=True),
                 sg.T('*Shutdown Main process, any activities / downloads will be cancelled', font='any 8')],

                [sg.T(' '), sg.Radio('Minimize App to systray', group_id='close_action', key='radio_minimize', enable_events=True),
                 sg.T('*Run in background, all activities / downloads will continue to run', font='any 8')],

                [sg.T(' '), sg.Radio('Quit (and close systray)', group_id='close_action', key='radio_quit', enable_events=True),
                 sg.T('*Shutdown down completely, including systray', font='any 8', size=(100, 1))],

            ])],

            [sg.T('', size=(1, 1))]
        ]

        update = [
            [sg.T(' ', size=(100, 1))],
            [sg.T('Check for update:'),
             sg.Combo(list(config.update_frequency_map.keys()), default_value=[k for k, v in config.update_frequency_map.items() if v == config.update_frequency][0],
                      size=(15, 1), key='update_frequency', enable_events=True)],
            [
                sg.B('', key=f'update_snp_mvp', image_data=refresh_icon, **transparent, tooltip='check for update'),
                sg.T(f'{config.APP_NAME} version = {config.APP_VERSION}', size=(50, 1), key=f'{config.APP_NAME}_version_note'),
            ],
            [
                sg.B('', key='update_youtube_dl', image_data=refresh_icon, **transparent,
                     tooltip=' check for update '),
                sg.T('Youtube-dl version = 00.00.00', size=(50, 1), key='youtube_dl_update_note'),
                sg.B('', key='rollback_ytdl_update', image_data=delete_icon, **transparent,
                     tooltip=' rollback youtube-dl update '),
            ],
            [sg.T('', size=(1, 14))]  # fill lines
        ]

        advanced = [

            [sg.T('')],
            [sg.T('Developer options: "*you should know what you are doing before modifying these options!"')],
            [sg.Checkbox('keep temp files / folders after done downloading for debugging.',
                         default=True if config.keep_temp else False, key='keep_temp', enable_events=True, )],
            [sg.Checkbox('Re-raise all caught exceptions / errors for debugging "Application will crash on any Error"',
                         default=True if config.TEST_MODE else False, key='TEST_MODE', enable_events=True,)],
        ]

        # layout ----------------------------------------------------------------------------------------------------
        layout = [
            [sg.T('', size=(70, 1)), ],
            [sg.TabGroup([[sg.Tab('General   ', general), sg.Tab('Network  ', network), sg.Tab('SysTray  ', systray),
                           sg.Tab('Update    ', update), sg.Tab('Advanced ', advanced)]],
                         tab_location='lefttop')]
        ]

        return layout

    def create_window(self):
        # main tab layout
        main_layout = self.create_main_tab()

        # Settings tab -------------------------------------------------------------------------------------------
        settings_layout = self.create_settings_tab()

        # log tab ------------------------------------------------------------------------------------------------
        log_layout = [[sg.T('Details events:')],
                      [sg.Multiline(default_text='', size=(70, 22), key='log', font='any 8', autoscroll=True)],

                      [sg.T('Log Level:'), sg.Combo([1, 2, 3], default_value=config.log_level, enable_events=True,
                                                    size=(3, 1), key='log_level',
                                                    tooltip='*(1=Standard, 2=Verbose, 3=Debugging)'),
                       sg.T(f'*saved to {config.sett_folder}', font='any 8', size=(75, 1),
                            tooltip=config.current_directory),
                       sg.Button('Clear Log')]]

        layout = [[sg.TabGroup(
            [[sg.Tab('Main', main_layout), sg.Tab('Settings', settings_layout),
              sg.Tab('Log', log_layout)]],
            key='tab_group')],
            [
             sg.T('', size=(73, 1), relief=sg.RELIEF_SUNKEN, font='any 8', key='status_bar'),
             sg.Text('', size=(10, 1), key='status_code', relief=sg.RELIEF_SUNKEN, font='any 8'),
             sg.T('⬇350 bytes/s', font='any 8', relief=sg.RELIEF_SUNKEN, size=(12, 1), key='total_speed'),
            ]
        ]

        # window
        window = sg.Window(title=config.APP_TITLE, layout=layout, size=(700, 450), margins=(2, 2),
                           return_keyboard_events=True)
        return window

    def start_window(self):
        self.active = True
        config.terminate = False

        self.window = self.create_window()
        self.window.Finalize()

        # override x button
        self.window.TKroot.protocol('WM_DELETE_WINDOW', self.close_callback)

        # expand elements to fit
        elements = ['url', 'name', 'folder', 'file_properties', 'update_note',
                    'log']  # elements to be expanded
        for element in elements:
            self.window[element].expand(expand_x=True)

        # log text, disable word wrap
        # use "undo='false'" disable tkinter caching to fix issue #59 "solve huge memory usage and app crash
        self.window['log'].Widget.config(wrap='none', undo='false')

        # bind mouse wheel for ('pl_menu' and 'stream_menu') only combo boxes, the rest combos are better without it
        def handler1(event):
            # pl_menu_mouse_wheel_handler
            try:
                i = event.widget.current()

                i = i - 1 if event.delta > 0 else i + 1
                if 0 <= i < len(self.playlist):
                    event.widget.current(i)
                    self.playlist_on_choice()
            except Exception as e:
                log('playlist menu handler', e, log_level=3)

        def handler2(event):
            # stream_menu_mouse_wheel_handler
            try:
                i = event.widget.current()

                i = i - 1 if event.delta > 0 else i + 1
                if 0 <= i < len(self.video.stream_menu if self.video else ''):
                    event.widget.current(i)
            except Exception as e:
                log('stream menu handler', e, log_level=3)

        def bind_mouse_wheel(combo, handler):
            # bind combobox to mousewheel
            self.window[combo].Widget.bind("<MouseWheel>", handler, add="+")  # for windows

            # for linux
            self.window[combo].Widget.bind("<ButtonPress-4>", handler, add="+")
            self.window[combo].Widget.bind("<ButtonPress-5>", handler, add="+")

        # systray radio buttons, assign default value
        self.window[f'radio_{config.close_action}'](True)

        # un hide active windows, if any
        self.un_hide_active_windows()

    def restart_window(self):
        try:
            # store log temporarily
            log = ''
            log = self.window['log'].get()

            self.window.Close()
        except:
            pass

        self.start_window()

        # restore log
        self.window['log'](log)


    def table_right_click(self, event):
        try:
            # select row under mouse
            id_ = self.window['table'].Widget.identify_row(event.y)  # first row = 1 not 0
            if id_:
                # mouse pointer over item
                self.window['table'].Widget.selection_set(id_)
                self.select_row(int(id_) - 1)  # get count start from zero
                self.window['table']._RightClickMenuCallback(event)
        except:
            pass

    def select_row(self, row_num):
        try:
            row_num = int(row_num)

            if self.selected_row_num != row_num:
                self.selected_row_num = row_num

                # get instant gui update, don't wait for scheduled update
                self.update_gui()

        except Exception as e:
            log('MainWindow.select_row(): ', e)

    def select_tab(self, tab_name=''):
        try:
            self.window[tab_name].Select()
        except Exception as e:
            print(e)

    @property
    def active_tab(self):
        # notebook
        nb = self.window['tab_group'].Widget

        # return active tab name
        return nb.tab(nb.select(), "text")

    def update_log(self):
        """
        read config.log_q and display text in log tab
        :return: None
        """
        # update log
        # read 10 messages max every time to prevent application freeze, in case of error messages flood by ffmpeg
        for _ in range(min(100, config.log_q.qsize())):
            line = config.log_q.get()
            try:
                contents = self.window['log'].get()
                # print(size_format(len(contents)))
                if len(contents) > config.max_log_size:
                    # delete 20% of contents to keep size under max_log_size
                    slice_size = int(config.max_log_size * 0.2)
                    self.window['log'](contents[slice_size:])

                self.window['log'](line, append=True)
            except Exception as e:
                # print('MainWindow.read_q() log error', e)
                pass

            self.set_status(line.strip('\n'))


    def on_table_click(self, event):
        selections = event.widget.selection()  # expected ('1', '2', '3', '4', '5', '6')

        # get selected rows starting from 0 and convert to int
        selections = [int(x) - 1 for x in selections]

        # we just use one selection in our application, will get the first one
        if selections:
            self.select_row(selections[0])

    def update_gui(self):
        """
        Periodically update gui widgets
        :return: None
        """
        if not self.active:
            return

        # handle url text change, time since last change only after 0.3 seconds, this prevent processing url with every
        # letter typed by user
        if 5 > time.time() - self.url_timer > 0.3:
            # set timer to negative value guarantee above condition to be false, i.e. execute one time only
            self.url_timer = -10
            self.on_url_text_change()

        # update Elements
        try:
            self.update_log()

            # update status code widget
            # self.window['status_code'](f'status: {self.d.status_code}')

            # file name
            # if self.window['name'].get() != self.d.name:  # it will prevent cursor jump to end when modifying name
            #     self.window['name'](self.d.name)

            # file_properties = f'Size: {size_format(self.d.total_size)} - Type: {self.d.type} - ' \
            #                   f'{", ".join(self.d.subtype_list)} - ' \
            #                   f'Protocol: {self.d.protocol} - Resumable: {"Yes" if self.d.resumable else "No"} ...'
            # self.window['file_properties'](file_properties)

            # Settings
            speed_limit = size_format(config.speed_limit) if config.speed_limit > 0 else "_no limit_"
            self.window['current_speed_limit'](f'Current value: {speed_limit}')

            self.window['youtube_dl_update_note'](
                f'Youtube-dl version = {config.ytdl_VERSION}, Latest version = {config.ytdl_LATEST_VERSION}')
            self.window[f'snp_mvp_version_note'](
                f'{config.APP_NAME} version = {config.APP_VERSION}, Latest version = {config.APP_LATEST_VERSION}')

            # # update total speed
            # total_speed = 0
            # for i in self.active_downloads:
            #     d = self.d_list[i]
            #     total_speed += d.speed
            # self.total_speed = f'⬇ {size_format(total_speed, "/s")}'
            # self.window['total_speed'](self.total_speed)

            # critical_settings_warning: sometimes user set proxy or speed limit in settings and forget it is
            # already set, which affect the whole application operation, will show a flashing text at main Tab
            if config.proxy or config.speed_limit:
                proxy = 'proxy: active, ' if config.proxy else ''
                sl = f'Speed Limit: {size_format(config.speed_limit)}' if config.speed_limit else ''
                self.window['critical_settings_warning'](proxy + sl)
                flip_visibility(self.window['critical_settings_warning'])
            else:
                self.window['critical_settings_warning']('', visible=False)

        except Exception as e:
            if config.TEST_MODE:
                raise e
            log('MainWindow.update_gui() error:', e)

    def set_status(self, text):
        """update status bar text widget"""
        try:
            self.window['status_bar'](text)

            # reset timer, used to clear status bar
            self.statusbar_timer = time.time()
        except:
            pass

    def change_theme(self):
        # theme
        sg.ChangeLookAndFeel(config.current_theme)

        # transparent color for button which mimic current background, will be use as a parameter, ex. **transparent
        global transparent
        transparent = dict(button_color=('black', sg.theme_background_color()), border_width=0)

    def fit_text(self, text, req_width):  # todo: replace all truncate usage with this method
        """
        truncate a text to a required width
        :param text: text to be truncated
        :param req_width: int, the required text width in characters
        :return: truncated text
        """

        # create tkinter font object, must pass a root window
        font = tkinter.font.Font(root=self.window.TKroot.master, font=default_font)

        # convert width in characters to width in pixels, tkinter uses '0' zero character as a default unit
        req_width = font.measure('0' * req_width)  # convert to pixels

        # measure text in pixels
        text_width = font.measure(text)

        if text_width <= req_width:
            return text

        # iterate and uses less character count until we get the target width
        length = len(text)
        while True:
            # will truncate text from the middle, see utils.truncate() for more info
            processed_text = truncate(text, length)
            if font.measure(processed_text) <= req_width or length <= 0:
                return processed_text

            length -= 1

    def show_properties(self, d):
        """
        Display properties of download item in a popup window
        :param d: DownloadItem object
        :return: None
        """
        try:

            if d:
                # General properties
                text = f'Name: {d.name} \n' \
                       f'Folder: {d.folder} \n' \
                       f'Progress: {d.progress}% \n' \
                       f'Downloaded: {size_format(d.downloaded)} \n' \
                       f'Total size: {size_format(d.total_size)} \n' \
                       f'Status: {d.status} \n' \
                       f'Resumable: {d.resumable} \n' \
                       f'Type: {d.type} - subtype: {", ".join(d.subtype_list)}\n'

                if d.type == 'video':
                    text += f'Protocol: {d.protocol} \n' \
                            f'Selected quality: {d.selected_quality}\n\n' \
                            f'Webpage url: {d.url}\n\n' \
                            f'Playlist title: {d.playlist_title}\n' \
                            f'Playlist url: {d.playlist_url}\n\n' \
                            f'Direct video url: {d.eff_url}\n\n' \
                            f'Direct audio url: {d.audio_url}\n\n'
                else:
                    text += f'Webpage url: {d.url}\n\n' \
                            f'Direct url: {d.eff_url}\n\n'

                sg.popup_scrolled(text, title='Download Item properties', size=(50, 20), non_blocking=True)
        except Exception as e:
            log('gui> properties>', e)

    # endregion

    def run(self):
        """main loop"""

        try:
            # todo: we could use callback style for some of these if's
            event, values = self.window.Read(timeout=50)
            if event and event not in ('__TIMEOUT__'):
                log(event, log_level=4)

            if event is None:
                # close or hide active windows
                if config.close_action == 'minimize':
                    self.hide()
                else:
                    self.close()

            # keyboard events --------------------------------------------------
            elif event.startswith('Up:'):  # up arrow example "Up:38"
                # get current element with focus
                focused_elem = self.window.find_element_with_focus()

                # for table, change selected row
                if self.window['table'] == focused_elem and self.selected_row_num > 0:
                    self.select_row(self.selected_row_num - 1)

            elif event.startswith('Down:'):  # down arrow example "Down:40"
                # get current element with focus
                focused_elem = self.window.find_element_with_focus()

                # for table, change selected row
                if self.window['table'] == focused_elem and self.selected_row_num < len(self.window['table'].Values)-1:
                    self.select_row(self.selected_row_num + 1)

            elif event.startswith('Delete:'):  # Delete:46
                # get current element with focus
                focused_elem = self.window.find_element_with_focus()

                # for table, change selected row
                if self.window['table'] == focused_elem and self.selected_d:
                    self.delete_btn()

            elif event.startswith('Escape:'):  # Escape:27

                # get current element with focus

                focused_elem = self.window.find_element_with_focus()

                # for table, change selected row

                if self.window['table'] == focused_elem and self.selected_d:
                    self.cancel_btn()

            # Mouse events MouseWheel:Up, MouseWheel:Down -----------------------
            elif event == 'MouseWheel:Up':
                pass
            elif event == 'MouseWheel:Down':
                pass

            # Main Tab ----------------------------------------------------------------------------------------
            elif event == 'update_note':
                # if clicked on update notification text
                if self.new_version_available:
                    self.update_app(remote=False)

            elif event == 'url':
                # reset timer, and self.url_text_change() will be called from update_gui()
                self.url_timer = time.time()

            elif event == 'copy url':
                url = values['url']
                if url:
                    clipboard.copy(url)

            elif event == 'paste url':
                self.window['url'](clipboard.paste().strip())
                self.on_url_text_change()

            elif event == 'Download':
                self.download_btn()

            elif event == 'folder':
                if values['folder']:
                    config.download_folder = os.path.abspath(values['folder'])
                else:  # in case of empty entries
                    self.window['folder'](config.download_folder)

            elif event == 'Retry':
                self.retry()


            # Settings tab -------------------------------------------------------------------------------------------
            elif event in ('about', 'app_icon', 'app_name'):  # about window
                # check if "about_window" is already opened
                found = [window for window in self.active_windows if isinstance(window, AboutWindow)]
                if found:
                    about_window = found[0]

                    # bring window to front
                    about_window.focus()

                else:  # not found
                    # create new window and append it to active windows
                    about_window = AboutWindow()
                    self.active_windows.append(about_window)

            elif event == 'themes':
                config.current_theme = values['themes']
                self.change_theme()

                # close all active windows
                for win in self.active_windows:
                    win.window.Close()
                self.active_windows.clear()

                self.restart_window()
                self.select_tab('Settings')

            elif event == 'show_thumbnail':
                config.show_thumbnail = values['show_thumbnail']

                self.reset_thumbnail()

            elif event == 'monitor':
                config.monitor_clipboard = values['monitor']

            elif event == 'show_download_window':
                config.show_download_window = values['show_download_window']

            elif event == 'auto_close_download_window':
                config.auto_close_download_window = values['auto_close_download_window']

            elif event == 'process_playlist':
                config.process_playlist = values['process_playlist']

            elif event == 'manually_select_dash_audio':
                config.manually_select_dash_audio = values['manually_select_dash_audio']

            elif event == 'segment_size':
                user_input = values['segment_size']

                # if no units entered will assume it KB
                try:
                    _ = int(user_input)  # will succeed if it has no string
                    user_input = f'{user_input} KB'
                except:
                    pass

                seg_size = parse_bytes(user_input)

                # set non valid values or zero to default
                if not seg_size:
                    seg_size = config.DEFAULT_SEGMENT_SIZE

                config.segment_size = seg_size
                self.window['seg_current_value'](f'current value: {size_format(config.segment_size)}')
                self.d.segment_size = seg_size

            elif event == 'sett_folder':
                selected = values['sett_folder']
                if selected == 'Local':
                    # choose local folder as a Settings folder
                    config.sett_folder = config.current_directory

                    # remove setting.cfg from global folder
                    delete_file(os.path.join(config.global_sett_folder, 'setting.cfg'))
                else:
                    # choose global folder as a setting folder
                    config.sett_folder = config.global_sett_folder

                    # remove setting.cfg from local folder
                    delete_file(os.path.join(config.current_directory, 'setting.cfg'))

                    # create global folder settings if it doesn't exist
                    if not os.path.isdir(config.global_sett_folder):
                        try:
                            choice = sg.popup_ok_cancel(f'folder: {config.global_sett_folder}\n'
                                                        f'will be created')
                            if choice != 'OK':
                                raise Exception('Operation Cancelled by User')
                            else:
                                os.mkdir(config.global_sett_folder)

                        except Exception as e:
                            log('global setting folder error:', e)
                            config.sett_folder = config.current_directory
                            sg.popup(f'Error while creating global settings folder\n'
                                     f'"{config.global_sett_folder}"\n'
                                     f'{str(e)}\n'
                                     f'local folder will be used instead')
                            self.window['sett_folder']('Local')
                            self.window['sett_folder_text'](config.sett_folder)

                # update display widget
                try:
                    self.window['sett_folder_text'](config.sett_folder)
                except:
                    pass

            # network------------------------------------------------
            elif event == 'speed_limit_switch':
                switch = values['speed_limit_switch']

                if switch:
                    self.window['speed_limit'](disabled=False)
                else:
                    config.speed_limit = 0
                    self.window['speed_limit']('', disabled=True)  # clear and disable

            elif event == 'speed_limit':
                sl = values['speed_limit']

                # if no units entered will assume it KB
                try:
                    _ = int(sl)  # will succeed if it has no string
                    sl = f'{sl} KB'
                except:
                    pass

                sl = parse_bytes(sl)
                config.speed_limit = sl

            elif event == 'max_concurrent_downloads':
                config.max_concurrent_downloads = int(values['max_concurrent_downloads'])

            elif event == 'max_connections':
                mc = int(values['max_connections'])
                if mc > 0:
                    config.max_connections = mc

            elif event in ('raw_proxy', 'http', 'https', 'socks4', 'socks5', 'proxy_type', 'enable_proxy'):
                self.set_proxy()

            elif event in ('use_referer', 'referer_url'):
                config.use_referer = values['use_referer']
                if config.use_referer:
                    self.window['referer_url'](disabled=False)
                    config.referer_url = self.window['referer_url'].get()
                else:
                    self.window['referer_url'](disabled=True)
                    config.referer_url = ''

            elif event in ('use_cookies', 'cookie_file_path'):
                config.use_cookies = values['use_cookies']
                if config.use_cookies:
                    self.window['cookie_file_path'](disabled=False)
                    config.cookie_file_path = self.window['cookie_file_path'].get()
                else:
                    self.window['cookie_file_path'](disabled=True)
                    config.cookie_file_path = ''

                # print(config.cookie_file_path)

            elif event in ('username', 'password', 'use_web_auth'):
                if values['use_web_auth']:
                    # enable widgets
                    self.window['username'](disabled=False)
                    self.window['password'](disabled=False)

                    config.username = values['username']
                    config.password = values['password']
                else:
                    config.username = ''
                    config.password = ''

                    # disable widgets
                    self.window['username'](disabled=True)
                    self.window['password'](disabled=True)

                # log('user, pass:', config.username, config.password)

            # update -------------------------------------------------
            elif event == 'update_frequency':
                selected = values['update_frequency']
                config.update_frequency = config.update_frequency_map[selected]  # selected
                # print('config.update_frequency:', config.update_frequency)

            elif event == 'update_youtube_dl':
                self.update_ytdl()

            elif event == 'rollback_ytdl_update':
                Thread(target=update.rollback_ytdl_update).start()
                self.select_tab('Log')

            elif event in [f'update_snp_mvp']:
                Thread(target=self.update_app, daemon=True).start()

            # systray -------------------------------------------------
            elif event in ('radio_close', 'radio_minimize', 'radio_quit'):
                config.close_action = event.replace('radio_', '')

            # Advanced -------------------------------------------------
            elif event == 'keep_temp':
                config.keep_temp = values['keep_temp']

            elif event == 'TEST_MODE':
                config.TEST_MODE = values['TEST_MODE']

            # log ---------------------------------------------------------------------------------------------------
            elif event == 'log_level':
                config.log_level = int(values['log_level'])
                log('Log Level changed to:', config.log_level)

            elif event == 'Clear Log':
                try:
                    self.window['log']('')
                except:
                    pass

            # Run every n seconds -----------------------------------------------------------------------------------
            if time.time() - self.timer1 >= 0.5:
                self.timer1 = time.time()

                # gui update
                self.update_gui()

                # read incoming requests and messages from queue
                self.read_q()

            # run active windows
            for win in self.active_windows:
                win.run()
            self.active_windows = [win for win in self.active_windows if win.active]  # update active list

            # run one time, reason this is here not in setup, is to minimize gui loading time
            if self.one_time:
                self.one_time = False

                # print last check for update
                if config.update_frequency < 0:
                    log('check for update is disabled!')

            # check for update block, negative values for config.last_update_check mean never check for update
            if config.update_frequency >= 0 and time.time() - self.check_for_update_timer >= 60:
                self.check_for_update_timer = time.time()

                t = time.localtime()
                today = t.tm_yday  # today number in the year range (1 to 366)

                if config.last_update_check == 0:  # no setting.cfg file found / fresh start
                    config.last_update_check = today
                else:
                    try:
                        if today < config.last_update_check:  # new year
                            days_since_last_update = today + 366 - config.last_update_check
                        else:
                            days_since_last_update = today - config.last_update_check

                        if days_since_last_update >= config.update_frequency:
                            log('days since last check for update:', days_since_last_update, 'day(s).')
                            log('asking user permission to check for update')
                            response = sg.PopupOKCancel(f'{config.APP_NAME} reminder to check for updates!',
                                                        f'days since last check: {days_since_last_update} day(s).',
                                                        'you can change frequency or disable check for update from settings\n', title='Reminder')
                            if response == 'OK':
                                # it will check for updates and offer auto-update for frozen app. version
                                Thread(target=self.update_app, daemon=True).start()
                                # Thread(target=self.check_for_update, daemon=True).start()
                                config.last_update_check = today
                            else:
                                config.last_update_check = 0
                                log('check for update cancelled by user, next reminder will be after',
                                    config.update_frequency, 'day(s).')
                    except Exception as e:
                        log('MainWindow.run()>', e)

            if time.time() - self.timer2 >= 1:
                self.timer2 = time.time()
                # update notification
                if self.new_version_available:
                    flip_visibility(self.window['update_note'])
                else:
                    self.window['update_note'](visible=False)

            # reset statusbar periodically
            if time.time() - self.statusbar_timer >= 10:
                self.statusbar_timer = time.time()
                self.set_status('')

        except Exception as e:
            log('Main window - Run()>', e)
            if config.TEST_MODE:
                raise e

    def download_btn(self, downloader=None):

        # get copy of current download item
        print("btn")

    # endregion

    @staticmethod
    def format_cell_data(k, v):
        """take key, value and prepare it for display in cell"""
        if k in ['size', 'total_size', 'downloaded']:
            v = size_format(v)
        elif k == 'speed':
            v = size_format(v, '/s')
        elif k in ('percent', 'progress'):
            v = f'{v}%' if v else '---'
        elif k == 'time_left':
            v = time_format(v)
        elif k == 'resumable':
            v = 'yes' if v else 'no'
        elif k == 'name':
            v = validate_file_name(v)

        return v

    def open_file_location(self):
        if self.selected_row_num is None:
            return

        d = self.selected_d

        try:
            folder = os.path.abspath(d.folder)
            file = d.target_file

            if config.operating_system == 'Windows':
                if not os.path.isfile(file):
                    os.startfile(folder)
                else:
                    cmd = f'explorer /select, "{file}"'
                    run_command(cmd)
            else:
                # linux
                cmd = f'xdg-open "{folder}"'
                run_command(cmd)
        except Exception as e:
            log('Main window> open_file_location>', e, log_level=2)

    def refresh_link_btn(self):
        if self.selected_row_num is None:
            return

        d = self.selected_d
        self.requested_quality = d.selected_quality
        config.download_folder = d.folder

        self.url = ''
        self.window['url'](d.url)
        self.on_url_text_change()

        self.window['folder'](config.download_folder)
        self.select_tab('Main')

    # endregion

    # region video

    def reset_thumbnail(self):
        """show a blank thumbnail background"""
        self.show_thumbnail(thumbnail=None)

    def show_thumbnail(self, thumbnail=None):
        """show video thumbnail in thumbnail image widget in main tab, call without parameter reset thumbnail"""

        try:
            if thumbnail is None:
                # reset thumbnail
                self.window['main_thumbnail'](data=thumbnail_icon)

            elif config.show_thumbnail and thumbnail != self.current_thumbnail:
                # new thumbnail
                self.window['main_thumbnail'](data=thumbnail)

            self.current_thumbnail = thumbnail
        except Exception as e:
            log('show_thumbnail()>', e)


    def set_tooltip(self, widget=None, tooltip_text=None):
        """
        change and Show tooltip without moving mouse pointer, correct tooltip glitches in case of dynamic changes
        :param widget: PySimpleGUI Element object, example window['mywidget']
        :param tooltip_text: text
        :return: None
        """

        try:
            # disable tooltip if no text
            if not tooltip_text:
                if widget.TooltipObject:
                    # widget still bounded to ToolTip.enter/leave , we can unbind it or simply mask schedule function
                    # for more details refer to PySimpleGUI "ToolTip" class
                    # self.widget.bind("<Enter>", self.enter)
                    # self.widget.bind("<Leave>", self.leave)
                    widget.TooltipObject.schedule = lambda: None
                return

            # add leading and trailing space for tooltip to look more natural
            tooltip_text = f' {tooltip_text} '

            # first hide any existing tooltip if any.
            if widget.TooltipObject:
                # call leave() "unschedule and hide" will cancel any sched. tooltip and hide current
                widget.TooltipObject.leave()

            # set new tooltip
            widget.set_tooltip(tooltip_text)

            # get current mouse x, y
            root = self.window.TKroot
            x, y = root.winfo_pointerxy()

            # find current widget under mouse
            widget_under_mouse = root.winfo_containing(x, y)

            # if our widget under mouse will show tooltip
            if widget.Widget == widget_under_mouse:
                # x,y position of our widget
                w_x, w_y = widget_under_mouse.winfo_rootx(), widget_under_mouse.winfo_rooty()

                # assign relative x, y to tooltip object
                widget.TooltipObject.x = x - w_x
                widget.TooltipObject.y = y - w_y

                # show tooltip now
                widget.TooltipObject.showtip()

        except Exception as e:
            log('set_tooltip()', e, log_level=3)

    def download_playlist(self):
        # check if playlist is ready
        if not self.playlist:
            sg.popup_ok('Playlist is empty, nothing to download :(', title='Playlist download')
            return

        # check if "subtitle_window" is already opened
        found = [window for window in self.active_windows if isinstance(window, PlaylistWindow)]
        if found:
            window = found[0]

            # bring window to front
            window.focus()

        else:  # not found
            window = PlaylistWindow(self.playlist)
            self.active_windows.append(window)

    def select_dash_audio(self):
        """prompt user to select dash audio manually"""
        if 'dash' not in self.d.subtype_list:
            log('select_dash_audio()> this function is available only for a dash video, ....')
            return

        audio_streams = [stream for stream in self.d.all_streams if stream.mediatype == 'audio']
        if not audio_streams:
            log('select_dash_audio()> there is no audio streams available, ....')
            return

        streams_menu = [stream.name for stream in audio_streams]
        layout = [
            [sg.T('Select audio stream to be merged with dash video:')],
            [sg.Combo(streams_menu, default_value=self.d.audio_stream.name, key='stream')],
            [sg.T('please note:\n'
                  'Selecting different audio format than video format, may takes longer time while merging')],
            [sg.T('')],
            [sg.Ok(), sg.Cancel()]
        ]

        window = sg.Window('Select dash audio', layout, finalize=True)

        # while True:
        event, values = window()

        if event == 'Ok':
            selected_stream_index = window['stream'].Widget.current()
            selected_stream = audio_streams[selected_stream_index]

            # set audio stream
            self.d.update_param(audio_stream=selected_stream)
            # print(self.d.audio_stream.name)
        window.close()

        # print(event, values)
    # endregion

    # region General
    def on_url_text_change(self):
        url = self.window['url'].get().strip()

        if url == self.url:
            return

        self.url = url

        # Focus and select main app page in case text changed from script
        self.window.BringToFront()
        self.select_tab('Main')

        # reset parameters and create new download item
        self.reset()
        try:
            self.set_cursor('busy')

        except Exception as e:
            log('url_text_change()> error', e)
            if config.TEST_MODE:
                raise e
        finally:
            self.set_cursor('default')

    def retry(self):
        self.url = ''
        self.on_url_text_change()

    def reset(self):
        # create new download item, the old one will be garbage collected by python interpreter

        # reset some values
        self.set_status('')  # status bar
        self.playlist = []
        self.video = None

        # widgets
        self.window['status_code']('')

        # abort youtube-dl current operation
        config.ytdl_abort = True

        # Force python garbage collector to free up memory
        gc.collect()

    def set_cursor(self, cursor='default'):
        # can't be called before window.Read()
        if cursor == 'busy':
            cursor_name = 'watch'
        else:  # default
            cursor_name = 'arrow'

        try:
            self.window.TKroot['cursor'] = cursor_name
        except:
            pass

    def close_callback(self):
        """This callback override main window close"""
        # currently "systray" support windows only
        if config.close_action == 'minimize' and config.systray_active:
            self.hide()

            # notify
            notify(f'{config.APP_NAME} still running in background', timeout=2)

        else:
            # closing window and terminate downloads
            self.active = False
            config.terminate = True

            if config.close_action == 'quit':
                config.shutdown = True

            root = self.window.TKroot

            root.quit()
            root.destroy()
            # self.window.RootNeedsDestroying = True
            # self.window.TKrootDestroyed = True

    def un_hide_active_windows(self):
        try:
            # un hide all active windows
            for obj in self.active_windows:
                obj.window.un_hide()
        except:
            pass

    def hide_active_windows(self):
        try:
            # hide all active windows
            for obj in self.active_windows:
                obj.window.hide()
        except:
            pass

    def hide(self):
        """close main window and hide other windows"""

        # hide active windows
        self.hide_active_windows()

        # hide main window
        self.window.hide()

    def un_hide(self):
        # show main window
        self.window.un_hide()

        # un hide active windows
        self.un_hide_active_windows()

    def close(self):
        """close window and stop updating"""
        self.active = False
        config.terminate = True

        # close active windows
        try:
            for obj in self.active_windows:
                obj.close()
        except:
            pass

        # log('main window closing')
        self.window.close()

        # Save setting to disk
        setting.save_setting()

        # Force python garbage collector to free up memory
        gc.collect()

    def check_scheduled(self):
        t = time.localtime()
        c_t = (t.tm_hour, t.tm_min)
        for d in self.d_list:
            if d.sched and d.sched[0] <= c_t[0] and d.sched[1] <= c_t[1]:
                self.start_download(d, silent=True)  # send for download
                d.sched = None  # cancel schedule time

    def ask_for_sched_time(self, msg=''):
        """Show a gui dialog to ask user for schedule time for download items, it take one or more of download items"""
        response = None

        layout = [
            [sg.T('schedule download item:')],
            [sg.T(msg)],
            [sg.Combo(values=list(range(1, 13)), default_value=1, size=(5, 1), key='hours'), sg.T('H  '),
             sg.Combo(values=list(range(0, 60)), default_value=0, size=(5, 1), key='minutes'), sg.T('m  '),
             sg.Combo(values=['AM', 'PM'], default_value='AM', size=(5, 1), key='am pm')],
            [sg.Ok(), sg.Cancel()]
        ]

        window = sg.Window('Scheduling download item', layout, finalize=True)

        e, v = window()

        if e == 'Ok':
            h = int(v['hours'])
            if v['am pm'] == 'AM' and h == 12:
                h = 0
            elif v['am pm'] == 'PM' and h != 12:
                h += 12

            m = int(v['minutes'])

            # # assign to download item
            # d.sched = (h, m)

            response = h, m

        window.close()
        return response

    def set_proxy(self):
        enable_proxy = self.window['enable_proxy'].get()
        config.enable_proxy = enable_proxy

        # enable disable proxy entry text
        self.window['raw_proxy'](disabled=not enable_proxy)

        if not enable_proxy:
            config.proxy = ''
            self.window['current_proxy_value']('_no proxy_')
            return

        # set raw proxy
        raw_proxy = self.window['raw_proxy'].get()
        config.raw_proxy = raw_proxy

        # proxy type
        config.proxy_type = self.window['proxy_type'].get()

        if raw_proxy:
            raw_proxy = raw_proxy.split('://')[-1]
            proxy = config.proxy_type + '://' + raw_proxy
        else:
            proxy = ''

        config.proxy = proxy
        self.window['current_proxy_value'](config.proxy)
        # print('config.proxy = ', config.proxy)

    # endregion

    # region update
    def check_for_update(self):
        self.set_cursor('busy')

        # check for update
        current_version = config.APP_VERSION
        info = update.get_changelog()

        if info:
            latest_version, version_description = info

            # compare with current application version
            newer_version = compare_versions(current_version, latest_version)  # return None if both equal # todo: use version_value instead
            # print(newer_version, current_version, latest_version)

            if not newer_version or newer_version == current_version:
                self.new_version_available = False
                log("check_for_update() --> App. is up-to-date, server version=", latest_version)
            else:  # newer_version available on server
                self.new_version_available = True

            # updaet global values
            config.APP_LATEST_VERSION = latest_version
            self.new_version_description = version_description
        else:
            self.new_version_description = None
            self.new_version_available = False

        # check for update batch for portable version only
        if config.FROZEN:
            info = update.get_update_batch_info()

            if info:
                minimum_version = info.get('minimum_version')
                max_version = info.get('max_version')
                hash = info.get('sha256')

                if version_value(max_version) >= version_value(config.APP_VERSION) >= version_value(minimum_version):
                    self.update_batch_available = True
                    self.update_batch_description = info.get('description', 'No description available')

                    # check if this batch already installed before, info will be stored in "update_batches_record" file
                    if os.path.isfile(config.update_batches_record):
                        with open(config.update_batches_record) as file:
                            if hash in file.read():
                                log('update batch already installed before')
                                self.update_batch_available = False
                                self.update_batch_description = ''

        self.set_cursor('default')

    def update_app(self, remote=True):
        """show changelog with latest version and ask user for update
        :param remote: bool, check remote server for update"""
        if remote:
            self.check_for_update()

        if self.new_version_available:
            # config.main_window_q.put(('show_update_gui', ''))
            execute_command('show_update_gui')
        elif self.update_batch_available:
            execute_command('show_update_gui', update_batch_window=True)
        else:
            if self.new_version_description:
                popup(f"App. is up-to-date, Local version: {config.APP_VERSION} \n"
                      f"Remote version:  {config.APP_LATEST_VERSION}", title='App update', )
            else:
                popup("couldn't check for update")

    def show_update_gui(self, update_batch_window=False):

        layout = [
            [sg.T('New update available:')],
            [sg.Multiline(self.update_batch_description if update_batch_window else self.new_version_description, size=(70, 10))],
            # show update button for Frozen versions only i.e. "windows portable version"
            [sg.B('Update') if config.FROZEN else sg.T(''), sg.B('website'), sg.Cancel()]
        ]

        window = sg.Window('Update Application', layout, finalize=True, keep_on_top=True)
        event, _ = window()
        if event == 'Update':
            Thread(target=update.update).start()
            self.select_tab('Log')
        elif event == 'website':
            update.open_update_link()

        window.close()

    def check_for_ytdl_update(self):
        config.ytdl_LATEST_VERSION = update.check_for_ytdl_update()
        log('youtube-dl, latest version = ', config.ytdl_LATEST_VERSION, ' - current version = ', config.ytdl_VERSION)

    def update_ytdl(self):
        current_version = config.ytdl_VERSION
        latest_version = config.ytdl_LATEST_VERSION or update.check_for_ytdl_update()
        if latest_version:
            config.ytdl_LATEST_VERSION = latest_version
            log('youtube-dl, latest version = ', latest_version, ' - current version = ', current_version)

            if latest_version != current_version:
                # select log tab
                self.select_tab('Log')

                response = sg.popup_ok_cancel(
                    f'Found new version of youtube-dl on github \n'
                    f'new version     =  {latest_version}\n'
                    f'current version =  {current_version} \n'
                    'Install new version?',
                    title='youtube-dl module update')

                if response == 'OK':
                    try:
                        Thread(target=update.update_youtube_dl).start()
                    except Exception as e:
                        log('failed to update youtube-dl module:', e)
            else:
                sg.popup_ok(f'youtube_dl is up-to-date, current version = {current_version}')
    # endregion

class AboutWindow:

    def __init__(self):
        self.active = True  # if False, object will be removed from "active windows list"

        # create gui
        msg1 = f'{config.APP_NAME} is an xxx app, \n' \
               f'Developed in Python, based on "xxxx", and "PySimpleGUI"  \n\n' \
               f'This application is free for use, in hope to be useful for someone, \n' \
               f'Conditions and usage restrictions:\n' \
               f'- This application is provided "AS IS" without any warranty, it is under no circumstances the {config.APP_NAME} author \n' \
               f'  could be held liable for any claim, or damages or responsible for any misuse of this application.\n\n' \
               f'your feedback is most welcomed on:'

        msg2 = f'Author,\n' \
               f'xxxx\n' \
               f'2019-202x'

        layout = [[sg.T(msg1)],
                  [sg.T('', font='any 1')],
                  [sg.T('Home page:', size=(10, 1)), sg.T(f'https://github.com/snp_mvp/snp_mvp', key='home_page', font='any 10 underline', enable_events=True)],
                  [sg.T('Issues:', size=(10, 1)),
                   sg.T(f'https://github.com/snp_mvp/snp_mvp/issues', key='issues', font='any 10 underline',
                        enable_events=True)],

                  [sg.T('Report a bug:', size=(10, 1)), sg.T(f'https://github.com/snp_mvp/snp_mvp/issues/new', key='new_issue', font='any 10 underline',
                                               enable_events=True), sg.T('*requires github account', font='any 8')],
                  [sg.T('Email:', size=(10, 1)), sg.T('xxx@xxx.com', key='email', font='any 10 underline', enable_events=True)],
                  [sg.T('', font='any 1')],
                  [sg.T(msg2)],
                  [sg.Column([[sg.Ok()]], justification='right')]]

        window = sg.Window(f'about {config.APP_NAME}', layout, finalize=True)

        # set cursor for links
        for key in ('home_page', 'issues', 'new_issue', 'email'):
            window[key].set_cursor('hand2')

        self.window = window

    def focus(self):
        self.window.BringToFront()

    def run(self):
        # read events
        event, values = self.window.read(timeout=10, timeout_key='_TIMEOUT_')

        if event in ('Ok', None):
            self.active = False
            self.window.close()

        elif event == 'home_page':
            webbrowser.open_new(f'https://github.com/snp_mvp/snp_mvp')

        elif event == 'issues':
            webbrowser.open_new(f'https://github.com/snp_mvp/snp_mvp/issues?q=is%3Aissue+')

        elif event == 'new_issue':
            webbrowser.open_new(f'https://github.com/snp_mvp/snp_mvp/issues/new')

        elif event == 'email':
            clipboard.copy('xxx@xxx.com')
            sg.PopupOK('Email "xxx@xxx.com" has been copied to clipboard\n')



class SysTray:
    """
    systray icon using pystray package
    """
    def __init__(self):
        self._active = False  # if systray works correctly
        self._tray_icon = os.path.join(config.sett_folder, 'systray.ico')  # path to icon
        self.icon = None
        self._hover_text = None

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        config.systray_active = value

    @staticmethod
    def show_main_window(icon, item):
        config.main_q.put('start_main_window')

    @staticmethod
    def minimize_to_systray(icon, item):
        config.main_q.put('minimize_to_systray')

    @staticmethod
    def close_to_systray(icon, item):
        config.main_q.put('close_to_systray')

    @property
    def tray_icon(self):
        """path to icon file"""
        try:
            # read base64 icon string into io buffer
            buffer = io.BytesIO(base64.b64decode(APP_ICON2))

            # open buffer by Pillow
            img = Image.open(buffer)

            if not os.path.isfile(self._tray_icon):
                # save file to settings folder
                img.save(self._tray_icon, format='ICO')

                # free memory
                # buffer.close()

            return img
        except Exception as e:
            raise e
            log('systray: tray_icon', e)

    def run(self):
        try:
            from pystray import Icon, Menu, MenuItem
            menu = Menu(MenuItem("Start / Show", self.show_main_window, default=True),
                        MenuItem("Minimize to Systray", self.minimize_to_systray),
                        MenuItem("Close to Systray", self.close_to_systray),
                        MenuItem("Quit", self.quit),)
            self.icon = Icon(config.APP_NAME, self.tray_icon, menu=menu)
            self.active = True
            self.icon.run()
        except Exception as e:
            log('systray: - run() - ', e)
            self.active = False

    def update(self, hover_text=None, icon=None):
        pass

    def shutdown(self):
        try:
            self.icon.stop()
        except:
            pass

    def quit(self, icon, item):
        """callback when selecting quit from systray menu"""
        # set global terminate flag
        self.shutdown()
        self.active = False
        config.terminate = True
        config.shutdown = True

