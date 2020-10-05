# autodeploy

## usage
.. code:: python
       
    from client import Client
    
    filename = 'deploy.sh'
    remote_path = '/tmp'
    
    with Client(host, username, password, port) as c:
        c.upload(filename, remote_path)
        dst_file = remote_path + '/' + filename
        r = c.execute('/usr/bin/sh {0}'.format(dst_file))
        print(r.stdout_text)
        print(r.stderr_text)
