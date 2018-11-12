#!/usr/bin/python
import BaseHTTPServer, SimpleHTTPServer, ssl, argparse, re
from tempfile import mkdtemp
from shutil import rmtree
from contextlib import contextmanager
from OpenSSL import crypto
from os.path import exists, join, abspath

@contextmanager
def TemporaryDirectory():
    name = mkdtemp()
    try:
        yield name
    finally:
        rmtree(name)

def CreateCert(HostName, KeyFile, CertFile):
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)
    c = crypto.X509()
    c.get_subject().C = 'XX'
    c.get_subject().ST = 'None'
    c.get_subject().L = 'None'
    c.get_subject().O = 'Simple Python Webserver Authority'
    c.get_subject().OU = 'Auto-generated Certificate'
    c.get_subject().CN = HostName
    c.set_serial_number(1000)
    c.gmtime_adj_notBefore(0)
    c.gmtime_adj_notAfter(315360000)
    c.set_issuer(c.get_subject())
    c.set_pubkey(k)
    c.sign(k, 'sha256')
    open(CertFile, "wt").write(crypto.dump_certificate(crypto.FILETYPE_PEM, c))
    open(KeyFile, "wt").write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

def RunServer(HostName, Port, KeyFile = None, CertFile = None, ClientCertCAs = None,
              HandlerClass = SimpleHTTPServer.SimpleHTTPRequestHandler,
              ServerClass = BaseHTTPServer.HTTPServer):
    HandlerClass.extensions_map.update({
        '.pac': 'application/x-ns-proxy-autoconfig'
    });
    
    httpd = ServerClass((HostName, Port), HandlerClass)
    
    if KeyFile is not None and CertFile is not None:
        if not exists(KeyFile) or not exists(CertFile):
            print "Generating Key and Certificate..."
            CreateCert(HostName, KeyFile, CertFile)
    
        if ClientCertCAs is None:
            httpd.socket = ssl.wrap_socket(httpd.socket, keyfile = KeyFile, certfile = CertFile, server_side = True)
        else:
            httpd.socket = ssl.wrap_socket(httpd.socket, keyfile = KeyFile, certfile = CertFile, server_side = True,
                                           cert_reqs = ssl.CERT_REQUIRED, ca_certs = ClientCertCAs)
        Proto = 'HTTPS'
    else:
        Proto = 'HTTP'

    sa = httpd.socket.getsockname()
    print "Serving", Proto, "on", sa[0], "port", sa[1], "..."
    if KeyFile is not None and CertFile is not None:
        print "    Cert:", abspath(CertFile)
    print ""
    httpd.serve_forever()

def Execute(SSL = False, HostName = None, Port = None, KeyFile = None, CertFile = None, ClientCertCAs = None,
         HandlerClass = SimpleHTTPServer.SimpleHTTPRequestHandler,
         ServerClass = BaseHTTPServer.HTTPServer):

    if HostName is None: HostName = 'localhost'
    if SSL is True:
        if Port is None: Port = 4443
        if KeyFile is None or CertFile is None:
            with TemporaryDirectory() as TempDir:
                RunServer(HostName, Port, join(TempDir, '%s.key' % HostName), join(TempDir, '%s.crt' % HostName), 
                          ClientCertCAs, HandlerClass, ServerClass)
        else:
            RunServer(HostName, Port, KeyFile, CertFile, ClientCertCAs, HandlerClass, ServerClass)
    else:
        if Port is None: Port = 8000
        RunServer(HostName, Port, None, None, None, HandlerClass, ServerClass)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = '''
            Launches a webserver (HTTP or HTTPS) that serves files from the local directory.  When run without
            arguments, this program functions like python's SimpleHTTPServer.  It adds support for HTTPS and client
            certificate authentication.  If needed, SSL certificates are generated on a one-time basis.
        ''',
        epilog = '''
            * If you specify only a certificate, then the key file is loaded from a file named identically, but with
            the extension '.key', so if you specify '--cert /path/to/file.crt', the key will be implied as
            '--key /path/to/file.key'.  If you specify '--certbase', then the extensions '.crt' and '.key' are
            added for you.
        '''
    )
    parser.add_argument('--ssl', action = 'store_true', dest = 'SSL', 
                        help = 'Launches an SSL (HTTPS) server (default: False)')
    parser.add_argument('--host', action = 'store', dest = 'HostName', 
                        help = 'Sets the host name to listen on (default: localhost)')
    parser.add_argument('--port', action = 'store', dest = 'Port', type = int,
                        help = 'Sets the port to listen on (default: 8000 for HTTP, 4443 for HTTPS)')
    parser.add_argument('--key', action = 'store', dest = 'KeyFile',
                        help = 'Sets the private key to use for SSL.  Implies --ssl (default: Temp-generated key*)')
    parser.add_argument('--cert', action = 'store', dest = 'CertFile',
                        help = '''Sets the public certificate to use for SSL.  Implies --ssl 
                                  (default: Temp-generated certificate*)''')
    parser.add_argument('--certbase', action = 'store', dest = 'CertBase',
                        help = 'Sets the base path to a certificate and key (default: None*)')
    parser.add_argument('--clientcerts', action = 'store', dest = 'ClientCertCAs',
                        help = 'Sets the CA to use for authenticating client certs.  Implies --ssl (default: None)')

    args = parser.parse_args()

    if args.CertBase is not None and args.CertFile is None:
        args.CertFile = '%s.crt' % args.CertBase
    if args.CertFile is not None and args.KeyFile is None:
        args.KeyFile = re.sub('\.[^\.]+$', '.key', args.CertFile)
    if args.KeyFile is not None or args.CertFile is not None or args.ClientCertCAs is not None:
        args.SSL = True
    Execute(args.SSL, args.HostName, args.Port, args.KeyFile, args.CertFile, args.ClientCertCAs)
