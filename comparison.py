# basic poc for text comparison

def compare_using_thebestspinner(text1, text2):
    import urllib3
    import urllib
    import re
    text1=urllib.parse.quote_plus(text1)
    text2=urllib.parse.quote_plus(text2)
    regex="' align=center>\r\n    (.*)\r\n.*<\/p>"
    headers = {"Pragma" : "no-cache",
    "Cache-Control" : "no-cache",
    "Origin" : "http://thebestspinner.com",
    "Content-Type" : "application/x-www-form-urlencoded",
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
    "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Referer" : "http://thebestspinner.com/compare/",
    "Accept-Encoding" : "gzip, deflate",
    "Accept-Language" : "en-US,en;q=0.9,he;q=0.8"}
    payload = f"text1={text1}&text2={text2}&action=compare"
    http = urllib3.PoolManager()
    resp = http.request("POST", "https://thebestspinner.com/compare/", headers=headers, body=payload)

    res = re.findall(regex, resp.data.decode())
    if len(res) > 0:
        return res[0]
    else: return -1