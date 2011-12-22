import os
import sys
import urllib
import urllib2
import getopt
import getpass
import urlparse

from BeautifulSoup import BeautifulSoup

class FileDownloader(object) :
  def __init__(self, url) :
    self.url = url
    self.is_proxy = False
    self.filetype = None
    self.scheme, self.host, self.path = url_parse(url[0])

  def set_proxy(self, user, pw, proxy) :
    self.user = user
    self.pw = pw
    self.proxy = proxy

  def set_filetype(self, filetype) :
    self.filetype = filetype

  def retrieve(self) :
    if self.filetype != None :
      html = url_open(self.url, {'user' : user, 'pw' : pw, 'proxy' : proxy})
      if html == '' :
        sys.exit(1) 
      links = parse_hyperlink(html, self.filetype)     
      total = len(links)
      for idx, link in enumerate(links) :
        scheme, host, path = url_parse(link)
        if host == '' :
          url = beautify_url(self.url[0], link)
        else :
          url = link

        try :
          print '%d/%d Downloading [%s]' % (idx + 1, total, url)
          urllib.urlretrieve(url, './%s' % os.path.basename(url))
        except IOError :
          print 'Fail saving file (%s)' % url
          sys.exit(1)
        urllib.urlcleanup()

def url_open(url, proxy_conf) :
  try :
    if proxy_conf :
      proxy = {'http' : proxy_conf['proxy']}
      proxy_handler = urllib2.ProxyHandler(proxy)
      opener = urllib2.build_opener(proxy_handler)
    else :
      opener = urllib2.build_opener()
  except urllib2.HTTPError, e :
    print >> sys.stderr, 'HTTP Error ', e, '%s' % url
  except urllib2.URLError, e :
    print >> sys.stderr, 'URL Error ', e, '%s' % url
  except :
    print '>> Unknown exception at urllib2.urlopen (%s)', url
    return
  html = opener.open(url[0]).read()
  return html

def url_parse(url) :
  url_part = urlparse.urlparse(url)
  scheme = url_part[0]
  host = url_part[1]
  path = urlparse.urlunparse(('', '') + url_part[2:])
  if path == '' :
    path = '/'
  return scheme, host, path

def beautify_url(url, link) :
  link_part = link.split('../')
  ndelim = len(link_part) - 1
  nsplit = ndelim + 1
  url_part = url.rsplit('/', nsplit)
  return url_part[0] + '/' + link_part[-1]

def parse_hyperlink(html, filetype) :
  links = list()
  soup = BeautifulSoup(html)

  for el in soup.findAll('a') :
    url = el['href']
    split_ext = url.rsplit('.', 1)
    if len(split_ext) > 1 :
      ext = split_ext[1]
      if (filetype != None) and (ext == filetype) :
        links.append(url)
  return links

def print_usage() :
  print "Usage: python %s [options...] URL" % sys.argv[0]
  print " -c/--crawl                     Retrieve all file in pages"
  print " -f/--filetype [file_extention] Set file extention which you want to retrieve"
  print " -p/--proxy [user@proxy_server] Set proxy and user"
  print " -h/--help                      This help text"

if __name__ == '__main__' :
  try :
    opts, args = getopt.getopt(sys.argv[1:], "p:cf:h", ["proxy=", "crawl", "filetype=", "help"])
  except getopt.error, msg :
    print "Usage: python %s [options...] URL" % sys.argv[0]
    sys.exit(2)    

  if len(args) < 1 :
    print "Usage: python %s [options...] URL" % sys.argv[0]
    sys.exit(2)

  url = args
  downloader = FileDownloader(url)
  print opts
  print args

  for o, a in opts :
    if o in ("--proxy", "-p") :
      if '@' in a :
        user, proxy = a.split('@')
        pw = getpass.getpass("%s@%s's password: " % (user, proxy))
        downloader.set_proxy(user, pw, proxy)
      else :
        print "Format: -p/--proxy [user@proxy_server]"
    elif o in ("--filetype", "-f") :
      filetype = a
      downloader.set_filetype(filetype)
    elif o in ("--help", "-h") :
      print_usage()

  downloader.retrieve()
