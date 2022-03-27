# basic poc for some news articles crawlers

####
#https://main.knesset.gov.il/Activity/committees/knesset/News/Pages/default.aspx
#
#http://www.knesset.gov.il/rssservice/daily_plenum_agenda.aspx
#http://www.knesset.gov.il/rssservice/daily_agenda.aspx
#http://www.knesset.gov.il/rssservice/plaw.aspx
#http://www.knesset.gov.il/rssservice/Vote.aspx
#http://www.knesset.gov.il/rssservice/mmm_material.aspx
#http://www.knesset.gov.il/rssservice/today_before.aspx
#http://www.knesset.gov.il/rssservice/committee_protocol.aspx
#http://www.knesset.gov.il/rssservice/plenum_protocol.aspx?t=2
#http://www.knesset.gov.il/rssservice/plenum_protocol.aspx
#http://www.knesset.gov.il/rssservice/eprotocol.aspx
#
#http://www.ynet.co.il/Integration/StoryRss2.xml
####

# this requires "pip install feedparser" to work
def get_ynet_rss_summaries():
    import feedparser
    url = "http://www.ynet.co.il/Integration/StoryRss2.xml"
    delim = "div>"
    result = {}
    news = feedparser.parse(url)

    print(news)

    for entry in news["entries"]:
        result[entry.title] = {}
        result[entry.title]['content'] = entry.summary.split(delim)[-1]
        result[entry.title]['date'] = entry.published_parsed

    return result

# not a good way to implement it
def gmail_scooper_client(username, password):
    import imaplib
    import email
    import urllib3
    from email.header import decode_header
    import re
    subject_regex = '.*h1>(.*?)<\/h1.*'
    body_regex = 'p>(.*)<\/p'
    result = {}
    imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    # will work until may 30 2022 - and needs to allow 'less secure 3rd party"
    imap.login(username, password)
    status, messages = imap.select("INBOX")
    for i in range(int(messages[0]), int(messages[0])-5, -1):
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding)
                if subject != "קיבלת סקופ מסקופר":
                    continue
                body = msg.get_payload(decode=True).decode()
                url = re.findall('.*d><a href="(.*?)".*', body)[0]
                http = urllib3.PoolManager()
                resp = http.request("GET", url)
                pr_subject = re.findall(subject_regex, resp.data.decode())[0]
                pr_body = re.findall(body_regex, resp.data.decode())[0]
                result[pr_subject] = {}
                result[pr_subject]['content'] = pr_body

    imap.close()
    imap.logout()
    return result

# better way to implement this crawler
def get_all_scooper_prs():
    import urllib3
    import re
    subject_regex = '.*h1>(.*?)<\/h1.*'
    body_regex = 'p>(.*)<\/p'
    b_still_works = True
    result = {}
    pr_index = int(open(r'\temp\scooper_pr_idx', 'r').read())
    while b_still_works:
        http = urllib3.PoolManager()
        resp = http.request("GET", f"https://www.scooper.co.il/pr/{pr_index}/")
        if resp.status == 200:
            pr_index += 1
            pr_subject = re.findall(subject_regex, resp.data.decode())[0]
            pr_body = re.findall(body_regex, resp.data.decode())[0]
            result[pr_subject] = {}
            result[pr_subject]['content'] = pr_body
        else: b_still_works = False
    open(r'\temp\scooper_pr_idx', 'w').write(str(pr_index))
    return result


def get_all_knesset_prs():
    import urllib3
    import re
    subject_regex =  ".*<h2.*>\r\n.*\r\n(.*)\r\n.*\r\n.*\r\n.*h2>.*"
    body_regex = 'p>(.*)<\/p'
    headers = {"accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding" : "gzip, deflate, br",
    "accept-language" : "en-US,en;q=0.9,he;q=0.8",
    "cache-control" : "no-cache",
    "pragma" : "no-cache",
    "cookie" : "rbzid=HlPBw+JKZixKP/Y/7GyoW8Up9x5ZCxOSyW4zvHs243Dd3nro58+URrTfh5reNMVnqCOrDjvO5XbPFe52MRiAW4ejjIWcCyhDIosC9NJ4QICl7gH0qjfmgm6y3wC0ga1jhaMTOaZHLVLn0/c9lYka7HEG37WLJMEX7IvL/z9e9lpLsBFCIAYpNweVgemSCtfU9q3mCS2A05Ky7t/IO+b2U/VGqIcROxSDCwvlajy0Cip44BDkRPkzgnbPclE4mNi5/dvLBMofn4H5c88xyXrgqqpNs2o5COyRp9wHLYk3FyY=; rbzsessionid=eac8faecdf8b7cc24a0f3b508f94e189; WSS_FullScreenMode=false",
    "sec-ch-ua" : '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    "sec-ch-ua-mobile" : "?0",
    "sec-ch-ua-platform" : '"Windows"',
    "sec-fetch-dest" : "document",
    "sec-fetch-mode" : "navigate",
    "sec-fetch-site" : "same-origin",
    "sec-fetch-user" : "?1",
    "upgrade-insecure-requests" : "1",
    "user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36"}
    result = {}
    pr_index = open(r'\temp\knesset_pr_idx', 'r').read()
    last_date =  datetime.datetime.strptime(pr_index, "%d%m%Y")

    while last_date <= datetime.datetime.now():
        url_fmt = last_date.strftime("%d%m%Y")
        last_date += datetime.timedelta(days=1)   

        http = urllib3.PoolManager()
        resp = http.request("GET", f"https://main.knesset.gov.il/Activity/committees/knesset/News/Pages/{url_fmt}.aspx", headers=headers)
        if resp.status == 200 and "X-Powered-By" in resp.headers:
            print( f"[+] worked - {url_fmt}.aspx")
            pr_subject = re.findall(subject_regex, resp.data.decode())[0].replace('\t','')
            #pr_body = re.findall(body_regex, resp.data.decode())[0]
            print(pr_subject)
            result[pr_subject] = {}
            #result[pr_subject]['content'] = pr_body
    open(r'\temp\knesset_pr_idx', 'w').write(last_date.strftime("%d%m%Y"))
    return result

