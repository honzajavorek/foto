# -*- coding: utf-8 -*-


import os
import sys
from tools.Config import Config


_BOLD = 1

_HIGHLIGHTS = dict(
    zip(['on_grey', 'on_red', 'on_green', 'on_yellow', 'on_blue', 'on_magenta', 'on_cyan', 'on_white'], range(40, 48))
)

_COLORS = dict(
    zip(['grey', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'], range(30, 38))
)

_RESET = '\033[0m'


def __colored(text=None, color=None, on_color=None, bold=None):
    if os.getenv('ANSI_COLORS_DISABLED') is None:
        format_string = '\033[%dm%s'
        if color is not None:
            text = format_string % (_COLORS[color], text)

        if on_color is not None:
            text = format_string % (_HIGHLIGHTS[on_color], text)

        if bold is not None:
            text = format_string % (_BOLD, text)
    text += _RESET
    return text


def __log(level, message):
    level = level.lower()
    is_visible = (level == 'error' or Config().getboolean('log', level) or Config().getboolean('application', 'debug'))
    is_quiet = Config().getboolean('application', 'quiet')
    if not is_quiet and is_visible:
        
        format_string = '[%s]'
        level = level.upper()
        
        if level == 'ERROR':
            text = __colored(format_string % level, 'red')
        elif level == 'WARNING':
            text = __colored(format_string % level, 'yellow')
        elif level == 'INFO':
            text = __colored(format_string % level, 'blue')
        elif level == 'OK':
            text = __colored(format_string % level, 'green')
        else:
            text = format_string % level
        
        if sys.stdin.encoding:
            text += (' ' + message.encode(sys.stdin.encoding))
        else:
            text += (' ' + message)
        
        print >> sys.stderr, text


def error(message):
    __log('error', message)


def warning(message):
    __log('warning', message)
    
    
def info(message):
    __log('info', message)


def ok(message):
    __log('ok', message)


