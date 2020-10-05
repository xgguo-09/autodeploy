# coding: utf-8

""" SSH client
实现了一些操作远程主机文件的 api
继承了 `session`
"""

import os
from os.path import join

try:
    from posix import error
except ModuleNotFoundError:
    pass

from session import Session

__all__ = ['Client']


class Client(Session):
    def __init__(self, host, username, password, port=22, timeout=None):
        super(Client, self).__init__(host, username, password, port, timeout)
        self._sftp = super(Client, self).sftp

    def execute(self, command, timeout=None):
        return super(Client, self).execute(command, timeout)

    def isdir(self, path):
        resp = self.execute('if [ -d {0} ]; then echo "1"; fi'.format(path))
        return resp.stdout_text == '1'

    def isfile(self, path):
        resp = self.execute('if [ -f {0} ]; then echo "1"; fi'.format(path))
        return resp.stdout_text == '1'

    def islink(self, path):
        resp = self.execute('if [ -L {0} ]; then echo "1"; fi'.format(path))
        return resp.stdout_text == '1'

    def verify_path(self, path):
        resp = self.execute('cd {0};'.format(path))
        if resp.stderr_text:
            raise ValueError('[<{}> path not exist]'.format(path))
        return path

    def listdir(self, path):
        return self._sftp.listdir(path)

    def listdir_attr(self, path):
        return self._sftp.listdir_attr(path)

    def listdir_iter(self, path):
        return self._sftp.listdir_iter(path)

    def chmod(self, path, mode):
        return self._sftp.chmod(path, mode)
    
    def mkdir(self, path, mode=511):
        try:
            self.verify_path(path)
        except ValueError as e:
            return self._sftp.mkdir(path, mode)

    def walk(self, top, topdown=True, onerror=None, followlinks=False):
        """
        like os.walk
        yields a 3-tuple
        dirpath, dirnames, filenames

        Example:
            >>> with Client('172.16.6.7', 'root', 'test') as c:
            >>>     for root, dirs, files in  c.walk('/root'):
            >>>         for f in files:
            >>>         print(join(root, f)
        """
        # top = self.verify_path(top)

        try:
            names = self.listdir(top)
        except error as err:
            if onerror is not None:
                onerror(err)
            return

        dirs, nondirs = [], []
        for name in names:
            if self.isdir(join(top, name)):
                dirs.append(name)
            else:
                nondirs.append(name)

        if topdown:
            yield top, dirs, nondirs

        for name in dirs:
            new_path = join(top, name)
            if followlinks or not self.islink(new_path):
                for x in self.walk(new_path, onerror, followlinks):
                    yield x
        if not topdown:
            yield top, dirs, nondirs

    def download(self, remote_file, local_path):
        dir_path, _ = os.path.split(local_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        _, filename = os.path.split(remote_file)
        self._sftp.get(remote_file, join(local_path, filename))

    def upload(self, local_file, remote_path):
        _, filename = os.path.split(local_file)
        self._sftp.put(local_file, join(remote_path, filename))

    def download_dir(self, remote_path, local_path):
        pass
    
    def upload_dir(self, local_path, remote_path):
        file_list = os.listdir(local_path)
        for filename in file_list:
            f = os.path.join(local_path, filename)
            self.upload(f, remote_path)
