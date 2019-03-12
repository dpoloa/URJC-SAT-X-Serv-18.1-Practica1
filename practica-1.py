#!/usr/bin/python3

# Created by:
# Daniel Polo Álvarez
# d.poloa@alumnos.urjc.es
# Subject: SAT (Servicios y Sistemas Telematicos)
# University: URJC (Universidad Rey Juan Carlos)

# This program obtains URLs and stocks them, returning a number that indicates the index of that URL in a
# dictionary.

# Modules importation

import sys
import socket
import webapp
import urllib.parse

# HTML pages

PAGE_MAIN_GET = """
<!DOCTYPE html>
<html lang="en">
  <body>
    <h2>Aplicacion web acortadora de URLs</h2>
    <p>Escribe aqui la web que quieres acortar:</p><p>
    <form action="/" method="post">
        URL: <input type="text" name="url" value="https://www.aulavirtual.urjc.es"><br><br>
        <input type="submit" value="Enviar">
    </form></p><p>
    <h4>---Lista de enlaces acortados---</h4>
    <table>
        <tr>
            <th>URL acortada</th>
            <th>URL real</th>
        <tr>
        {dicc}
    </table>
  </body>
</html>
"""

PAGE_REDIRECT = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta http-equiv="Refresh" content="0; url={url}" />
  </head>
  <body>
    <h2>Aplicacion web acortadora de URLs</h2>
    <p>Redirigiendo en 5 segundos...</p>
    <p>Si la redireccion no funciona, pulsa <a href={url}>aqui</a></p>
  </body>
</html>
"""

PAGE_ERROR = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta http-equiv="Refresh" content="5; url=http://localhost:1234/" />
  </head>
  <body>
    <h2>Aplicacion web acortadora de URLs</h2>
    <p>{msg}</p>
  </body>
</html>
"""

PAGE_RETURN_URL = """
<!DOCTYPE html>
<html lang="en">
  <body>
    <h2>Aplicacion web acortadora de URLs</h2>
    <p>URL introducida: <a href={url1}>{url1}</a></p>
    <p>URL acortada: <a href={url2}>{url2}</a></p>
  </body>
</html>
"""

# Python global variable

count = 0

# Python dictionaries

shortUrlDict = {}
longUrlDict = {}

# Program code

myPort = 1234
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
mySocket.bind(('localhost', myPort))


class URLApp(webapp.WebApp):

    def parse(self, request):

        return request.split(' ', 2) + request.split('\r\n\r\n')

    def process(self, parsed_request):

        global count

        html_method = parsed_request[0]
        html_resource = parsed_request[1]
        html_body = parsed_request[4]

        url = ""
        url_real = ""
        html_msg = ""
        html_code = ""
        html_page = ""
        resource = 0

        if html_method == "GET":
            if html_resource == "/":
                html_code = "200 OK"
                for urlshort in shortUrlDict:
                    html_msg = html_msg + "<tr><td>" + urlshort + "</td><td>" + shortUrlDict[urlshort] + "</td></tr>"

                html_page = PAGE_MAIN_GET.format(dicc=html_msg)
            else:
                error = False
                try:
                    resource = int(html_resource[1:])
                except ValueError:
                    error = True
                    html_msg = "El recurso introducido no es un numero. Introduce un numero correcto."
                    html_code = "400 Bad Request"
                    html_page = PAGE_ERROR.format(msg=html_msg)

                if not error:
                    try:
                        urlshort = "http://localhost:1234/" + str(resource)
                        urlreal = shortUrlDict[urlshort]
                        html_code = "301 Moved Permanently"
                        html_page = PAGE_REDIRECT.format(url=urlreal)
                    except KeyError:
                        html_msg = ("El recurso introducido no esta incluido en el diccionario." +
                                    "Por favor, introduce un nuevo recurso.")
                        html_code = "400 Bad Request"
                        html_page = PAGE_ERROR.format(msg=html_msg)

        elif html_method == "POST":
            if html_resource == '/':
                found = True
                try:
                    url = urllib.parse.parse_qs(html_body, encoding='utf-8')['url'][0]
                    if (not url.startswith("http://")) and (not url.startswith("https://")):
                        url = "http://" + url
                except KeyError:
                    found = False

                if found:
                    urlmatch = True
                    try:
                        url_real = longUrlDict[url]
                    except KeyError:
                        urlmatch = False
                        newurl = "http://localhost:1234/" + str(count)
                        shortUrlDict[newurl] = url
                        longUrlDict[url] = newurl
                        html_code = "200 OK"
                        html_page = PAGE_RETURN_URL.format(url1=url, url2=newurl)
                        count += 1

                    if urlmatch:
                        html_code = "200 OK"
                        html_page = PAGE_RETURN_URL.format(url1=url, url2=url_real)
                else:
                    html_msg = ("El unico recurso POST aceptado es el / usando su formulario.<br>" +
                                "Se redirigira a la pagina principal")
                    html_code = "400 Bad Request"
                    html_page = PAGE_ERROR.format(msg=html_msg)

            else:
                html_msg = ("El unico recurso POST aceptado es el / usando su formulario.<br>" +
                            "Se redirigira a la pagina principal")
                html_code = "400 Bad Request"
                html_page = PAGE_ERROR.format(msg=html_msg)

        return html_code, html_page


if __name__ == "__main__":
    try:
        testWebApp = URLApp("localhost", 1234)
    except KeyboardInterrupt:
        print("\n---> Finishing...")
        sys.exit(0)
