"""
    PyIDM

    multi-connections internet download manager, based on "pyCuRL/curl", "youtube_dl", and "PySimpleGUI"

    :copyright: (c) 2019-2020 by Mahmoud Elshahat.
    :license: GNU LGPLv3, see LICENSE for more details.
"""

# configurations
from queue import Queue
import os
import sys
import platform

from .version import __version__


# CONSTANTS
APP_NAME = 'PyIDM'
APP_VERSION = __version__ 
APP_TITLE = f'{APP_NAME} version {APP_VERSION} .. an open source download manager'
DEFAULT_DOWNLOAD_FOLDER = os.path.join(os.path.expanduser("~"), 'Downloads')
DEFAULT_THEME = 'DarkGrey2'
DEFAULT_CONNECTIONS = 10
DEFAULT_SEGMENT_SIZE = 524288  # in bytes  = 512 KB
DEFAULT_CONCURRENT_CONNECTIONS = 3
APP_URL = 'https://github.com/pyIDM/pyIDM'
LATEST_RELEASE_URL = 'https://github.com/pyIDM/pyIDM/releases/latest'

# headers, note: a random user agent will replace below value later by video.import_ytdl()
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3721.3'
HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-us,en;q=0.5',
}

DEFAULT_LOG_LEVEL = 2

APP_LATEST_VERSION = None  # get value from update module
ytdl_VERSION = 'loading ...'  # will be loaded once youtube-dl get imported
ytdl_LATEST_VERSION = None  # get value from update module

TEST_MODE = False
FROZEN = getattr(sys, "frozen", False)  # check if app is being compiled by cx_freeze
# -------------------------------------------------------------------------------------

# current operating system  ('Windows', 'Linux', 'Darwin')
operating_system = platform.system()
operating_system_info = f'{platform.platform()} - {platform.machine()}'   # i.e. Win7-64 and Vista-32

# application exit flag
terminate = False  # for main window and downloads
shutdown = False  # complete shutdown flag

# settings parameters

# General
current_theme = DEFAULT_THEME
all_themes = []
monitor_clipboard = True
show_download_window = True
auto_close_download_window = True
segment_size = DEFAULT_SEGMENT_SIZE  # in bytes
show_thumbnail = True  # auto preview video thumbnail at main tab
process_playlist = False  # fetch videos info only if selected, since big playlist consume time/resources.
big_playlist_length = 50  # minimum number of videos in big playlist, it will ignore "process_playlist"
manually_select_dash_audio = False  # if True, will prompt user to select audio format for dash video

# connection / network
speed_limit = 0  # in bytes, zero == no limit
max_concurrent_downloads = DEFAULT_CONCURRENT_CONNECTIONS
max_connections = DEFAULT_CONNECTIONS
use_referer = False
referer_url = ''  # referer website url

# website authentication
use_web_auth = False
username = ''
password = ''

# proxy
proxy = ''  # must be string example: 127.0.0.1:8080
proxy_type = 'http'  # socks4, socks5
raw_proxy = ''  # unprocessed from user input
enable_proxy = False

# logging
log_entry = ''  # one log line
max_log_size = 1024 * 1024 * 5  # 5 MB
log_level = DEFAULT_LOG_LEVEL  # standard=1, verbose=2, debug=3
log_recorder_q = Queue()

# use_cookies
use_cookies = False
cookie_file_path = ''

# systray
close_action = 'quit'  # close, minimize, to systray, or quit and close systray
systray_active = False

# youtube-dl abort flag, will be used by decorated YoutubeDl.urlopen(), see video.import_ytdl()
ytdl_abort = False

# advanced
keep_temp = False  # keep temp files / folders after done downloading for debugging

# -------------------------------------------------------------------------------------

# folders
if hasattr(sys, 'frozen'):  # like if application froen by cx_freeze
    current_directory = os.path.dirname(sys.executable)
else:
    path = os.path.realpath(os.path.abspath(__file__))
    current_directory = os.path.dirname(path)
sys.path.insert(0, os.path.dirname(current_directory))
sys.path.insert(0, current_directory)

sett_folder = None
global_sett_folder = None
download_folder = DEFAULT_DOWNLOAD_FOLDER

# ffmpeg
ffmpeg_actual_path = None
ffmpeg_download_folder = sett_folder

# downloads
active_downloads = set()  # indexes for active downloading items
d_list = []


# update
update_frequency = 7  # 'every day'=1, every week=7, every month=30 and so on
last_update_check = 0  # day number in the year range from 1 to 366
update_frequency_map = {'Everyday': 1, 'Every Week': 7, 'Every Month': 30, 'Never': -1}
update_batches_record = os.path.join(current_directory, 'update_batches_record.info')


# queues
main_q = Queue()  # used by pyIDM.py
main_window_q = Queue()  # queue for Main application window
log_q = Queue()  # queue to hold log messages to be displayed in main window's log tab
commands_q = Queue()  # queue to access MainWindow internal methods from threads
error_q = Queue()  # used by workers to report server refuse connection errors
jobs_q = Queue()  # # required for failed worker jobs

# settings parameters to be saved on disk
settings_keys = ['current_theme', 'monitor_clipboard', 'show_download_window', 'auto_close_download_window',
                 'segment_size', 'show_thumbnail', 'speed_limit', 'max_concurrent_downloads', 'max_connections',
                 'update_frequency', 'last_update_check', 'proxy', 'proxy_type', 'raw_proxy', 'enable_proxy',
                 'log_level', 'download_folder', 'manually_select_dash_audio',
                 'use_referer', 'referer_url', 'close_action', 'process_playlist', 'keep_temp']

# -------------------------------------------------------------------------------------


# status class as an Enum
class Status:
    """used to identify status, work as an Enum"""
    downloading = 'downloading'
    cancelled = 'cancelled'
    completed = 'completed'
    pending = 'pending'
    processing = 'processing'  # for any ffmpeg operation
    error = 'error'
