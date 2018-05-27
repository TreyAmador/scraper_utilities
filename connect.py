# scraper utility
from bs4 import BeautifulSoup
from requests import exceptions
import requests
import socket
import time


def connect(url):

    ERR_SHORT = 10
    ERR_LONG = 30
    MAX_ERRORS = 10

    error_counter = 0

    def handle_errors(err, url, dur=0, res=None):
        print('Error!', err, 'at url', url, sep='\n')
        if res:
            print('Status code error is', res.status_code)
        print('Resuming in ', dur, 'sec...')
        error_counter += 1
        time.sleep(dur)

    def timeout_error(err, url, wait_time):
        handle_errors(err, url, wait_time)

    def redirect_error(err, res, url, wait_time):
        handle_errors(err, url, wait_time, res)
        return url

    def attribute_error(err, res, url):
        handle_errors(err, url, 0, res)

    def connection_success(res, url):
        print('Successfully connected to', res.url)
        return BeautifulSoup(res.text,'lxml'), res

    while error_counter < MAX_ERRORS:
        try:
            res = requests.get(url, timeout=1.0)
            res.raise_for_status()
        except exceptions.ConnectTimeout as err:
            timeout_error(err, url, ERR_SHORT)
        except exceptions.ReadTimeout as err:
            timeout_error(err, url, ERR_SHORT)
        except exceptions.Timeout as err:
            timeout_error(err, url, ERR_LONG)
        except socket.timeout as err:
            timeout_error(err, url, ERR_LONG)
        except exceptions.HTTPError as err:
            url = redirect_error(err, res, url, ERR_SHORT)
        except exceptions.TooManyRedirects as err:
            url = redirect_error(err, res, url, ERR_SHORT)
        except exceptions.ConnectionError as err:
            timeout_error(err, url, ERR_LONG)
        except exceptions.URLRequired as err:
            url = redirect_error(err, res, url, ERR_SHORT)
        except TypeError as err:
            attribute_error(err, res, url)
        except ValueError as err:
            attribute_error(err, res, url)
        except AttributeError as err:
            attribute_error(err, res, url)
        except socket.error as err:
            timeout_error(err, url, ERR_LONG)
        except exceptions.RequestException as err:
            timeout_error(err, url, ERR_LONG)
        else: 
            return connection_success(res, url)
    return None, None

