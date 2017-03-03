# -*- coding: utf-8 -*-
# utility functions for web scraper
from bs4 import BeautifulSoup,Tag
from requests import exceptions
from collections import deque
import requests
import socket
import pprint
import time
import sys
import re


class WebsiteMap:


    class Path:

        def __init__(self,curr,prev,good,red):
            self.current = curr
            self.previous = prev
            self.redirect = red == True


    def __init__(self):
        pass



class URLQueue:
    ''' a store for the history of a website '''
    ''' could be used to map website? '''


    def __init__(self):
        self._queue = deque()


    def push_front(self,elem):
        self._queue.append(elem)


    def pop_front(self):
        if not self.is_empty():
            return self._queue.pop()


    def front(self):
        return self._queue[-1]


    def push_rear(self,elem):
        self._queue.appendleft(elem)


    def pop_rear(self):
        if not self.is_empty():
            return self._queue.popleft()


    def rear(self):
        return self._queue[0]


    def is_empty(self):
        return len(self._queue) == 0


    def query_recent(self,num):
        return [self._queue[-(i+1)] for i in range(num) if i < len(self._queue)]



class Scrutil:
    ''' additional utility functions for webscraping '''


    def __init__(self,*urls):
        self._queue = URLQueue()
        self._urls = []
        self.add_base_urls(list(urls))


    def add_base_urls(self,url):
        if isinstance(url,list):
            self._urls += url
        elif isinstance(url,tuple):
            self._urls += list(url)
        elif isinstance(url,str):
            self._urls.append(url)


    def connect(self,url):
        ''' retrieve BeautifulSoup and res for webpage '''

        def handle_errors(errors,err,url,dur):
            print('Error\n',err,'\nat url\n',url)
            errors.append(err)
            print('This is consecutive error',len(errors))
            print('Resuming in ',dur,'sec')
            time.sleep(dur)

        def timeout_error(errors,err,url,dur):
            handle_errors(errors,err,url,dur)

        def redirect_error(res,queue,errors,err,url,dur):
            print('Status code error is',res.status_code)
            handle_errors(errors,err,url,dur)
            return redirect(queue,0)

        def attribute_error(errors,err,res,url):
            handle_errors(errors,err,url,0)

        def redirect(queue,num):
            if not queue.is_empty():
                return queue.pop_front()
            elif self._urls:
                return self._urls[num]
            else:
                return None

        def success(queue,res,url):
            print('Successfully connected to',res.url)
            queue.push_front(res.url)
            return BeautifulSoup(res.text,'lxml'), res


        errors = []
        max_errors = 50
        short, long = 10, 30
        while len(errors) < max_errors:
            try:
                res = requests.get(url,timeout=1.0)
                res.raise_for_status()
            except exceptions.ConnectTimeout as err:
                timeout_error(errors,err,url,short)
            except exceptions.ReadTimeout as err:
                timeout_error(errors,err,url,short)
            except exceptions.Timeout as err:
                timeout_error(errors,err,url,long)
            except socket.timeout as err:
                timeout_error(errors,err,url,long)
            except exceptions.HTTPError as err: # make this more specific?
                url = redirect_error(res,self._queue,errors,err,url,short)
            except exceptions.TooManyRedirects as err:
                url = redirect_error(res,self._queue,errors,err,url,short)
            except exceptions.ConnectionError as err:
                timeout_error(errors,err,url,long)
            except exceptions.URLRequired as err:
                url = redirect_error(res,self._queue,errors,err,url,short)
            except TypeError as err:
                attribute_error(errors,err,res,url)
            except ValueError as err:
                attribute_error(errors,err,res,url)
            except AttributeError as err:
                attribute_error(errors,err,res,url)
            except socket.error as err:
                timeout_error(errors,err,url,long)
            except exceptions.RequestException as err:
                timeout_error(errors,err,url,long)
            else:
                errors.clear()
                return success(self._queue,res,url)
            finally:
                pass
        return None,None


def mongo_clean(text):
    if isinstance(text,str):
        return re.sub(r'^\$',r'~$',text).replace('.','*')
    return str(text)


def tag_to_text(tag):
    try:
        if isinstance(tag,Tag):
            return tag.get_text()
        elif isinstance(tag,str):
            return tag
        elif isinstance(tag,int):
            return str(tag)
    except (TypeError,ValueError):
        return None
    except AttributeError:
        return None


def gather_links(tags):
    if isinstance(tags,Tag):
        return [a['href'] for a in tags.find_all('a') if a.has_attr('href')]
    return []


def gather_attrs(html,tag,attr):
    if isinstance(html,Tag):
        return [t[attr] for t in html.find_all(tag) if t.has_attr(attr)]
    return []


def gather_links_desctructive(tags):
    links = gather_links(tags)
    if links:
        tags.decompose()
    return links


# this needs some fidelity!
def pprint_safe(obj):
    pp = pprint.PrettyPrinter()
    try:
        pp.pprint(obj)
    except UnicodeEncodeError:
        pp.pprint(str(obj).encode('utf-8'))
    except UnicodeError:
        pp.pprint(str(obj).encode('utf-8'))
    except TypeError:
        print('type error')
    finally:
        pass


def print_safe(*text,sep=' ',end='\n'):

    def unicode_print(text,sep=' ',end='\n'):
        try:
            if isinstance(text,str):
                print(text.encode('utf-8'),sep='',end=sep)
        except (TypeError,ValueError,AttributeError):
            print('Output object skipped...')

    for txt in text:
        try:
            print(txt,sep='',end=sep)
        except UnicodeEncodeError as err:
            unicode_print(txt)
        except UnicodeDecodeError as err:
            unicode_print(txt)
        except UnicodeError as err:
            unicode_print(txt)
    print('',sep='',end=end)


# make higher fidelity!
def pprint_safe(obj):
    try:
        pprint.pprint(obj)
    except UnicodeEncodeError as err:
        print('Unicode encode error, entry skipped')
    except UnicodeError as err:
        print('Unicode error, entry skipped')
    except (ValueError,AttributeError):
        print('Unknown printing error')

