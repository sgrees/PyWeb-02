import socket
import sys
import os
import mimetypes


def response_ok(body=b"this is a pretty minimal response", mimetype=b"text/plain"):
    """returns a basic HTTP response"""
    # TODO: Update response_ok so that it uses the provided body
    # and mimetype.
    resp = []
    resp.append(b"HTTP/1.1 200 OK")
    resp.append(b"".join(["Content-Type: ", mimetype]))
    resp.append(b"")
    resp.append(b"this is a pretty minimal response")
    return b"\r\n".join(resp)


def response_method_not_allowed():
    """returns a 405 Method Not Allowed response"""
    resp = []
    resp.append(b"HTTP/1.1 405 Method Not Allowed")
    resp.append(b"")
    return b"\r\n".join(resp)


def response_not_found():
    """returns a 404 Not Found response"""
    # TODO: Consruct and return a 404 response.
    #
    # See response_method_not_allowed for an example of
    # another type of 4xx response. You will need to use
    # the correct number (by changing "405") and also the
    # correct statement (by changing "Method Not Allowed").
    resp = []
    resp.append(b"HTTP/1.1 404 Not Found")
    resp.append(b"")
    return b"\r\n".join(resp)


def parse_request(request):
    first_line = request.split("\r\n", 1)[0]
    method, uri, protocol = first_line.split()
    if method != "GET":
        raise NotImplementedError("We only accept GET")
    return uri


def resolve_uri(uri):
    """Returns appropriate content and a mime type for uri.
    If the requested URI is a directory, returns plain-text listing of
        contents with mimetype `text/plain`.
    If the URI is a file, returns contents of that file and correct mimetype.
    If the URI does not map to a real location, raises an
        exception that the server can catch to return a 404 response.
    """
    # TODO: Raise a NameError if the requested content is not present
    # under webroot.
    # TODO: Fill in the appropriate content and mime_type give the URI.
    # See the assignment guidelines for help on "mapping mime-types", though
    # you might need to create a special case for handling make_time.py
    webroot = "webroot/"
    try:
        if os.path.isfile(webroot + uri):
            mime_type = mimetypes.guess_type(webroot + uri)
            with open(webroot + uri, 'rb') as f:
                content = f.read()
        else:
            mime_type = b'text/plain'
            content = "\r\n".join(os.listdir(webroot + uri)).encode('utf8')
    except IOError:
        raise NameError("Resource doesn't exist")
    return content, mime_type


def server(log_buffer=sys.stderr):
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()  # blocking
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)
                request = ''
                while True:
                    data = conn.recv(1024)
                    request += data
                    if len(data) < 1024:
                        break
                try:
                    uri = parse_request(request)
                except NotImplementedError:
                    response = response_method_not_allowed()
                else:
                    try:
                        content, mime_type = resolve_uri(uri)
                    except NameError:
                        response = response_not_found()
                    else:
                        response = response_ok(content, mime_type)

                print('sending response', file=log_buffer)
                conn.sendall(response)
            finally:
                conn.close()

    except KeyboardInterrupt:
        sock.close()
        return


if __name__ == '__main__':
    server()
    sys.exit(0)
