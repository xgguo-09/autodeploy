# coding: utf-8

""" SSH 会话管理
封装了第三方 SSH 库 `paramiko`

 `Session` 主要函数：
    - `execute`: 执行一条命令，执行完即关闭连接
    - `invoke_sell`：调用一个 shell 会话
    - `sftp`: 打开 sftp 客户端
"""

import paramiko
from paramiko.util import ClosingContextManager

from compat import bytes2str
from utils import lazy_property

__all__ = ['Session', 'Response']


class Response(object):
    """A command's response"""

    def __init__(self):
        self.command = None
        self.stderr = None
        self.stdout = None

    @lazy_property
    def stdout_text(self):
        out = self.stdout.read()
        return bytes2str(out).strip()

    @lazy_property
    def stderr_text(self):
        err = self.stderr.read()
        return bytes2str(err).strip()

    @lazy_property
    def ok(self):
        return self.stderr_text == ''

    def __repr__(self):
        if len(self.command):
            return '<Response [{0}]>'.format(self.command)
        else:
            return '<Response>'


class Session(ClosingContextManager):
    __ssh = paramiko.SSHClient()
    __ssh.load_system_host_keys()
    __ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def __init__(self, host, username, password, port=22, timeout=None):
        self._ssh = self.__ssh
        self._chan = None

        self.host = host
        self.port = port
        self._login(username, password, timeout)
        self._closed = False

    def __getattr__(self, name):
        if hasattr(self._ssh, name):
            return getattr(self._ssh, name)
        elif hasattr(self.sftp, name):
            return getattr(self.sftp, name)
        else:
            raise AttributeError('<not found [{}]>'.format(name))

    def __repr__(self):
        return '<Session [{0}]>'.format(self.host)

    def _login(self, username, password, timeout=None):
        self._ssh.connect(
            hostname=self.host,
            port=self.port,
            username=username,
            password=password,
            timeout=timeout
        )

    @property
    def sftp(self):
        t = self._ssh.get_transport()
        return paramiko.SFTPClient.from_transport(t)

    @property
    def closed(self):
        return self._closed

    def close(self):
        if self._chan:
            self._chan.close()
        try:
            self.sftp.close()
        except OSError:
            try:
                self._ssh.close()
            except:
                pass
        finally:
            self._closed = True

    def invoke_sell(self, term='vt100', width=80, height=24, width_pixels=0,
                    height_pixels=0, environment=None):
        if self._chan is None:
            self._chan = self._ssh.invoke_shell(
                term,
                width,
                height,
                width_pixels,
                height_pixels,
                environment
            )
        return self._chan

    def execute(self, command, timeout=None):
        stdin, stdout, stderr = self._ssh.exec_command(command, timeout=timeout)
        cmd = command
        r = Response()
        r.command = cmd
        r.stdout = stdout
        r.stderr = stderr
        return r
