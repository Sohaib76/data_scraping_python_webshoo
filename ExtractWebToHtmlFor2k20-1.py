import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from lxml import html
import boto3
import os
from PIL import Image
import numpy as np
import jinja2
import time
from bs4 import BeautifulSoup
import urllib.request
import json
import xml.dom.minidom as md
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from progress.bar import Bar
from urllib.request import urlopen
import re
import sys
import shutil
from time import gmtime, strftime
from datetime import date
import unidecode
import traceback
import logging


# handle error send mail
# extract html comment
# mainController uncomment
# for url[1:2]
#del the_url
# -------------------------------------------
xmlurl = ""
visitDomain = ""
oldDomain = ""
server = ""
k1 = ""
k2 = ""
lastdonejson = ""
sitemapMain = ""
noOfRecProcessed = 0
fileCurrentLoc = ""
startTime = ''
theLastHtmlTimeStamp = 0
theFirstHtmlTimeStamp = 0
editedFirstHtmlTimeStamp = ''
editedtheLastHtmlTimeStamp = ''
visitingUrl = ''

# https://customstoday.com/sitemap-posttype-post.2013.xml


def sendMail(ErrorfileName):
    fromaddr = "notificationsctd@gmail.com"
    toaddr = "ebrahym@muhammadi.me"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Subject of the Mail"
    filename = ErrorfileName
    attachment = open(filename, "rb")
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromaddr, "notificationsctd.password")
    text = msg.as_string()
    s.sendmail(fromaddr, toaddr, text)
    s.quit()


def exitProgram(dateTimeEnd, xmlFileUsed, startTime, endTime, noOfRecProcessed, editedFirstHtmlTimeStamp, editedtheLastHtmlTimeStamp, visitingUrl):
    logf = open("logFile.txt", 'a+')
    logf.write("{0} , {1} , {2} , {3} , {4} , {5}\n".format(
        startTime, xmlFileUsed, visitingUrl, editedFirstHtmlTimeStamp, editedtheLastHtmlTimeStamp, str(noOfRecProcessed)))
    logf.close()
    exit()


def handleError(errorM, doExit=True):

    today = date.today()
    endTime = strftime(str(today)+"T%X+00:00", gmtime())
    erroLog = open("errorLog.txt", 'a+')
    erroLog.write("{0} , {1} , {2} , {3} , {4} , {5}\n".format(
        startTime, errorM, visitingUrl, editedFirstHtmlTimeStamp, editedtheLastHtmlTimeStamp, str(noOfRecProcessed)+" Files Processed"))
    erroLog.close()
    sendMail("errorLog.txt")  # UNCOMMENT IT
    if doExit == True:
        exit()


def parseforPythonJson():
    global xmlurl
    global visitDomain
    global oldDomain
    global server
    global k1
    global k2
    global lastdonejson
    global sitemapMain
    global errorXml
    global imageDomain
    try:
        js = open("forPython.json", "r")
        jsonResponse = json.loads(js.read())
    except Exception as e:
        errorM = str(e)
        print(errorM)
        handleError(errorM)
    xmlurl = jsonResponse["xmlurl"]
    visitDomain = jsonResponse["visitDomain"]
    oldDomain = jsonResponse["oldDomain"]
    server = jsonResponse["server"]
    k1 = jsonResponse["k1"]
    k2 = jsonResponse["k2"]
    lastdonejson = jsonResponse["lastdonejson"]
    sitemapMain = jsonResponse["sitemapMain"]
    errorXml = jsonResponse["errorXml"]
    try:
        j = urlopen(
            'https://ctdjson.ams3.digitaloceanspaces.com/params.json')
        jsonResponse = json.loads(j.read().decode())
    except Exception as e:
        errorM = str(e)
        print(errorM)
        handleError(errorM)
    imageDomain = jsonResponse["imageDomain"]


def convertDateTimeToTimeStamp(inputTime):
    try:
        x = pd.Timestamp(str(inputTime))
    except Exception as e:
        errorM = str(e)
        print(errorM)
        handleError(errorM)
    return pd.Timestamp.timestamp(x)


def extractData(url):

    p_images_urls = []
    tagTexts = []
    tagUrls = []
    metas = []
    pTagsDiv = []
    print("****************** Visiting URL {0} *****************".format(url))

    r = requests.get(url)
    if r.status_code == 200:
        data = r.text
        soup = BeautifulSoup(data, 'html.parser')
    else:
        errorM = "response status not 200"
        handleError(errorM, False)
        print("Error")
        print(url)

    try:
        pTagsDiv = soup.find("div", class_="entry")
        print(pTagsDiv)
        pTagsDiv = str(pTagsDiv)
        if "iframe" in str(pTagsDiv) or "img" in str(pTagsDiv):
            pTagsDiv = str(pTagsDiv).replace("<noscript>", "")
            pTagsDiv = str(pTagsDiv).replace("</noscript>", "")
            print(pTagsDiv)

    except:
        errorM = "Error getting div"
        handleError(errorM, False)

    try:

        p_images = soup.find("div", class_="entry").findAll('img')
        print("Finding Images Inside P Tag:")
        for image in p_images:
            if image["src"][0] == "h":
                print("url", image["src"])
                p_images_urls.append(image["src"])

    except:

        print("No Image Tags In Paragraph")

    try:
        headerText = soup.find("h1", class_="entry-title").get_text()
        print("Heading:\t", headerText)

        reportedBY = soup.find("p", class_="post-meta").get_text()
        print("Reported By:\t", reportedBY)

        imageUrl = soup.find("img", class_="attachment-slider")["src"]
        print("Topic Image:\t", imageUrl)
        imageUrlTitle = soup.find("img", class_="attachment-slider")["title"]
        print(imageUrlTitle)
        imageUrlAlt = soup.find("img", class_="attachment-slider")["alt"]
        print(imageUrlAlt)

        metaTags = soup.findAll("meta")
        print("MetaTags:")
    except Exception as e:
        errorM = str(e)
        print(errorM)
        handleError(errorM, False)
    for meta in metaTags:
        metaProperty = meta.get("property")
        if str(metaProperty)[0] == "o":
            metas.append(meta)
            print(meta)

    titleTag = soup.find("title")
    title = titleTag.get_text()
    print("Title:\t", title)

    try:
        tags = soup.findAll(attrs={"rel": "tag"})
        print("Tags:")
        for tag in tags:
            tagText = tag.get_text()
            tagTexts.append(tagText)
            tagUrl = tag["href"]
            tagUrls.append(tagUrl)
            print("Tag Text: ", tag.get_text(), "\t,\t", end=" ")
            print("Tag Url: ", tag["href"],)
    except:
        print("No Tags")

    # Category Get
    categoryUrlList = []
    categories = soup.find("article")["class"]
    # print(cat)
    for category in categories:
        if "category" in category:
            # change with visit domain
            categoryUrlList.append(
                visitDomain + "/category/"+category.split("-")[1] + "/")

    return unidecode.unidecode(str(pTagsDiv)), headerText, reportedBY, metas, title, tagTexts, tagUrls, p_images_urls, imageUrl, imageUrlTitle, imageUrlAlt, categoryUrlList


# url = "https://customstoday.com/fbr-transfers-206-pcs-officers-officials-with-immediate-effect/"
# url = "https://customstoday.com/collector-preventive-ahmad-rauf-transfers-superintendents-appraisers-inspectors/"
# url = "https://customstoday.com/customs-today-issue-03-march-to-09-march-2020/"
# extractData(url)


def optimizeImage(imageUrl, nameOfConvertedImg):

    img_data = requests.get(imageUrl).content
    with open("downloaded.jpg", 'wb') as handler:
        handler.write(img_data)
    img = Image.open('downloaded.jpg').convert('RGB')
    img.save(nameOfConvertedImg, 'jpeg', optimize=True)  # quality=20


def createHtml(metas, title, headerText, pathImage, reportedBY, modified_p_images_url, pTagsDiv, tagUrlTxtZipped, categoryUrlTxtZipped, imageUrlTitle, imageUrlAlt):
    template = jinja2.Template("""

   <!DOCTYPE html>
    <html lang="en">
    <head>
        <script data-ad-client="ca-pub-1195724557739662" async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
    
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-100928152-4"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());

            gtag('config', 'UA-100928152-4');
        </script>

        <script src="https://ctdscr.ams3.digitaloceanspaces.com/special.js"></script>
        <meta charset="utf-8" />
        <meta
        name="viewport"
        content="width=device-width, initial-scale=1, shrink-to-fit=no"
        />
        <meta name="description" content="" />
        <meta name="author" content="" />
        {% for Meta_Tag in Meta_Tags %}
        {{Meta_Tag}}
        {% endfor %}
        <title>{{Title}}</title>

    <!-- Latest compiled and minified CSS -->

    <!-- CSS only -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css" integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk" crossorigin="anonymous">

    <script src="https://use.fontawesome.com/d093cd7f46.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/handlebars.js/2.0.0/handlebars.js"></script>
    </head>

    <body>
        <!-- Navigation -->
        <nav
        class="navbar navbar-expand-lg navbar-dark bg-dark"
        style="margin-top: 0px; "
        >

        <div class="container">
            <span style="color: aliceblue; margin:15px; font-size: 0.8rem; margin-top: 20px;" >
            <!-- 20px -->
            <script>document.write(Date().substring(0, 15));</script>
            </span>
            <div class="social-icon-container"

            >
            <script id="socialIconsContainer" type="text/x-handlebars-template">
                {{hbsocial_icons_for}}
                <a class="navbar-brand" href="{{hbsocial_icons_imageUrl}}">
                    <i style='width: 2px; font-size: 0.8rem;' class="{{hbsocial_icons_icon}}" aria-hidden="true"></i>
                    <!-- 8px -->
                </a>
                {{hbsocial_icons_for_end}}
            </script>
            </div>



            <button
            class="navbar-toggler"
            type="button"
            data-toggle="collapse"
            data-target="#navbarResponsive"
            aria-controls="navbarResponsive"
            aria-expanded="false"
            aria-label="Toggle navigation"
            >
            <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarResponsive">
            <ul class="navbar-nav ml-auto">

                <script id="headerTitlesContainer" type="text/x-handlebars-template">
                    {{hbheader_titles_for}}
                    <li class="nav-item">
                    <a class="nav-link" href="{{hbheader_titles_textUrl}}">{{hbheader_titles_text}}</a>
                    </li>
                    {{hbheader_titles_for_end}}
                </script>

                </li>

            </ul>
            </div>
        </div>
        </nav>
        <div class="container">
        <div class="row" style="padding: 2%;">
            <div class="col-8 col-md-4" style="margin-left: 0px; padding-left: 35px;" >

            <a href="">
            <img

            class="img-fluid"

                src="https://ctdimg.ams3.digitaloceanspaces.com/custom-log2.png"
                alt="Logo"
            />


            </a>
            </div>
            <div class="col-12 col-md-8" style="padding:0px">
            <!-- md-8 -->
            <a href="http://glogisticsonline.com/"> <img
            class="img-fluid"


                src="https://ctdimg.ams3.digitaloceanspaces.com/custom-banner.jpg"
                alt="Global Clearance and Logistics"
            />
            <!-- https://customstoday.com/wp-content/uploads/2019/03/resize-web-banner.jpg -->
            </a>

            </div>
            <div
            style="
                margin-top: 10px;
                margin-bottom: 5px;
                height: 1px;
                width: 100%;
                border-top: 1px solid gray;
            "
            ></div>
        </div>
        </div>

        <!-- Page Content -->
        <div class="container">
        <div class="row">
            <!-- Post Content Column -->
            <div class="col-lg-8">
            <!-- Title -->
            <h1 class="mt-4" style="font-size: 2rem;">
                {{Header_Text}}
            </h1>

            <br/>


            <div class="row text-center" style="align-items: center; justify-content: center;">
            <img
                class="img-fluid w-100"
                title={{imageUrlTitle}}
                src={{Main_Img}}
                alt={{imageUrlAlt}}

            />
            </div>

            <br/>
            <br/>
            <!-- Post Content -->
            <p class="lead">
                {{Reported_By}}
            </p>
            {{P_Tags_Div}}

            
      



            <br/>

            </div>

            <!-- Search Widget -->
            <div class="col-md-4">
            <script
                async
                src="https://cse.google.com/cse.js?cx=001909707626927524296:rgofoagmcge"
            ></script>
            <div class="gcse-search"></div>

            <!-- Side Widget -->
            <div class="card my-4" >
                <h5 class="card-header">In Other Stories</h5>

                <!-- ------------------------------------------------------- -->
                <div class="the-container"

                >
                <script
                    id="otherStoriesContainer"
                    type="text/x-handlebars-template"
                >

                    {{hburls_for}}

                    <div class="card-body row"
                    style="margin-left: 0px;"
                    >

                    <div class="col-4" style="padding:0px;">
                        <a href="{{hburls_url}}">
                        <img

                        class="img-fluid"
                        src="{{hburls_urlimage}}" />

                        </a>
                    </div>

                        <div class="col-8">
                        <a href="{{hburls_url}}">
                        <p style="font-size: 1rem; line-height: 1rem;">{{hburls_title}}</p>
                        </a>
                        </div>
                    </div>
                    {{hburls_for_end}}
                </script>
                </div>

                <!-- ----------------------------------------------------------- -->
            </div>
            </div>




            <uL style="list-style: none; margin:20px; margin-left:-20px">
                {% for catTexts, catUrls in categoryUrlTxtZipped %}

                <a href={{catUrls}}><li class="text-dark">{{catTexts}}</li></a>

                {% endfor %}
            </uL>

            <uL style="list-style: none; margin:20px; margin-left:-20px">
                {% for tagTexts, tagUrls in tagUrlTxtZipped %}

                <a href={{tagUrls}}><li class="text-dark">{{tagTexts}}</li></a>

                {% endfor %}
            </uL>


                <!-- <uL style="list-style: none; margin:20px; margin-left:-20px">
                    <li class="text-dark">Sample 1</li>
                <li class="text-dark">Sample 1</li>
                <li class="text-dark">Sample 1</li>
                </uL>  -->



        </div>
        <!-- /.row -->
        </div>

        <!-- Footer -->
        <footer class="py-4 bg-dark">


        <div class="container-fluid">

            <p class="m-0 text-center text-white"
            style="font-size: 0.8rem;"
            >
            Customs Today (C) Copyright 2020, All Rights Reserved
            </p>
        </div>
        </footer>

    <!-- JS, Popper.js, and jQuery -->
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js" integrity="sha384-OgVRvuATP1z7JjHLkuOU7Xw704+h835Lr+6QL9UvYjZE3Ipu6Tp75j7Bh/kR0JKI" crossorigin="anonymous"></script>


        <script src="https://ctdscr.ams3.digitaloceanspaces.com/script.js"></script>
        <!-- ../../scripts/script.js -->
        <!-- https://ctdscr.ams3.digitaloceanspaces.com/script.js-->
    </body>
    </html>
    """)

    #  {% for P_Tag_Div in P_Tags_Div %}
    #         <p><p>
    #        {% endfor %}

    #     {% for P_Tag_Img in P_Tags_Img %}
    #       <p><img class="img-fluid" src="{{P_Tag_Img}}" alt=""/></p>
    #     {% endfor %}

    try:
        theHtmlTemplate = template.render(
            {"hbsocial_icons_for": "{{#each socialIcons}}",
             "hbsocial_icons_for_end": "{{/each}}",
             "hbsocial_icons_imageUrl": "{{imageUrl}}",
             "hbsocial_icons_icon": "{{iconClass}}",
             "hbheader_titles_for": "{{#each headerTitles}}",
             "hbheader_titles_for_end": "{{/each}}",
             "hbheader_titles_textUrl": "{{textUrl}}",
             "hbheader_titles_text": "{{text}}",
             "hburls_for": "{{#each urls}}",
             "hburls_for_end": "{{/each}}",
             "hburls_url": "{{url}}",
             "hburls_urlimage": "{{urlimage}}",
             "hburls_title": "{{title}}",
             "Meta_Tags": metas,
             "Title": title,
             "Header_Text": headerText,
             #  "Main_Img": "https://ctdimg.ams3.cdn.digitaloceanspaces.com/"+pathImage,
             "Main_Img": imageDomain+pathImage,
             "Reported_By": reportedBY,
             "P_Tags_Img": modified_p_images_url,
             "P_Tags_Div": pTagsDiv,
             "tagUrlTxtZipped": tagUrlTxtZipped,
             "imageUrlTitle": imageUrlTitle,
             "imageUrlAlt": imageUrlTitle,
             "categoryUrlTxtZipped": categoryUrlTxtZipped


             })
    except Exception as e:
        errorM = str(e)
        print(errorM)
        handleError(errorM)
    return theHtmlTemplate


def uploadingToAmazon(htmlFolder, images_path):

    session = boto3.session.Session()
    client = session.client('s3',
                            region_name='ams3',
                            endpoint_url="https://"+server,
                            aws_access_key_id=k1,
                            aws_secret_access_key=k2)

    fileObj = open(htmlFolder, "rb")

    client.put_object(Bucket='ctdweb',
                      Key=htmlFolder,
                      Body=fileObj,
                      ACL='public-read',
                      ContentType='text/html'

                      )
    fileObj.close()

    for imagedirectory in images_path:
        fileObj = open(imagedirectory, "rb")
        client.put_object(Bucket='ctdimg',
                          Key=imagedirectory,
                          Body=fileObj,
                          ACL='public-read',
                          ContentType='image/jpeg',
                          CacheControl="public, max-age=604800"

                          )


def writeToSiteMap(fileName, urlloc, currentTime):
    tree = ET.parse(fileName)
    # print(tree)
    root = tree.getroot()

    urlObjectsString = []
    for url in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
        urlObjectsString.append(ET.tostring(url).decode("utf-8"))

    newObjectString = '\n\t<url> \n\t\t<loc>{0}</loc> \n\t\t<lastmod>{1}</lastmod> \n\t\t<changefreq>daily</changefreq> \n\t\t<priority>1</priority></url>\n'.format(
        urlloc, currentTime)

    structure = """<?xml version="1.0" encoding="UTF-8"?>
    <?xml-stylesheet type="text/xsl" href="https://customstoday.com/wp-content/plugins/xml-sitemap-feed/includes/xsl/sitemap.xsl.php?ver=4.3.2"?>
    <!-- generated-on="2020-07-14T10:52:22+00:00" -->
    <!-- generator="XML & Google News Sitemap Feed plugin for WordPress" -->
    <!-- generator-url="http://status301.net/wordpress-plugins/xml-sitemap-feed/" -->
    <!-- generator-version="4.3.2" -->
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd
        http://www.google.com/schemas/sitemap-image/1.1
        http://www.google.com/schemas/sitemap-image/1.1/sitemap-image.xsd">
    """

    oldUrlObject = ' '.join(urlObjectsString).replace(
        "<ns0:", "<").replace("</ns0:", "</").replace("&gt;", "").replace(' xmlns:ns0="http://www.sitemaps.org/schemas/sitemap/0.9">', '>')
    updatedObjectString = structure + newObjectString + oldUrlObject + "</urlset>"
    # print(updatedObjectString)

    fil = open(fileName, "w+")
    fil.write(updatedObjectString)
    fil.close()


def mainController():
    global noOfRecProcessed
    global startTime
    global theLastHtmlTimeStamp
    global theFirstHtmlTimeStamp
    global editedFirstHtmlTimeStamp
    global editedtheLastHtmlTimeStamp
    global visitingUrl

    print("\n******************** Welcome To Website Recreation Program *********************************\n\n")

    today = date.today()
    startTime = strftime(str(today)+"T%X+00:00", gmtime())

    print("\n******************** Reading From forPython.json *******************************************\n")

    bar = Bar('Processing', max=2)
    for i in range(2):
        parseforPythonJson()
        bar.next()
    bar.finish()

    response = requests.get(xmlurl)
    soup = BeautifulSoup(response.content, 'lxml')

    urls = soup.findAll("url")
    counter = len(urls)
    if lastdonejson != 0:

        for url in urls[::-1]:
            counter -= 1
            urltime = url.find("lastmod").get_text()

            if lastdonejson == urltime:
                print("Counter Length", counter)
                break

    print("\n******************** Visting Urls And Fetching Data ** ****************************************\n")

    ind = 0
    if counter == 0:
        return

    for url in urls[counter-1::-1]:  # counter
        currentTime = strftime(str(today)+"T%X+00:00", gmtime())
        lastTimeStamp = url.find("lastmod").get_text()
        the_url = url.find("loc").get_text()

        #the_url = "https://customstoday.com/dg-valuation-issues-customs-values-of-engine-parts-vide-vr-1446-2020-2/"
        # the_url = "https://customstoday.com/fbr-updates-withholding-income-tax-rates-for-exporters/"
        # the_url = "https://customstoday.com/bajwa-seems-overwhelmingly-impressed-by-turkish-tax-system/"
        # the_url = "https://customstoday.com/fbr-transfers-206-pcs-officers-officials-with-immediate-effect/"
        # the_url = "https://customstoday.com.pk/fbr-transfers-206-pcs-officers-officials-with-immediate-effect/"
        # the_url = "https://customstoday.com/customs-today-issue-03-march-to-09-march-2020/"
        # the_url = "https://customstoday.com/various-organizations-made-duty-bound-to-allow-real-time-access-fbr"
        # the_url = "https://customstoday.com/fbr-announces-updated-wht-rates-for-imported-goods"
        oldEditedDomain = oldDomain + "/" + the_url.split("/")[3] + "/"
        editedUrl = visitDomain + "/" + the_url.split("/")[3] + "/"

        try:
            pTagsDiv, headerText, reportedBY, metas, title, tagTexts, tagUrls, p_images_urls, imageUrl, imageUrlTitle, imageUrlAlt, categoryUrlList = extractData(
                oldEditedDomain)
        except:
            print("except")
            # try:
            #     client.download_file('ctdjson',
            #                          errorXml,
            #                          errorXml)  # "siteMap.xml"
            try:
                f = open(errorXml)
            # Do something with the file
            except IOError:

                filee = open(errorXml, "w+")
                structure = """<?xml version="1.0" encoding="UTF-8"?>
                <?xml-stylesheet type="text/xsl" href="https://customstoday.com/wp-content/plugins/xml-sitemap-feed/includes/xsl/sitemap.xsl.php?ver=4.3.2"?>
                <!-- generated-on="2020-07-14T10:52:22+00:00" -->
                <!-- generator="XML & Google News Sitemap Feed plugin for WordPress" -->
                <!-- generator-url="http://status301.net/wordpress-plugins/xml-sitemap-feed/" -->
                <!-- generator-version="4.3.2" -->
                <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                    xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                    xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
                    http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd
                    http://www.google.com/schemas/sitemap-image/1.1
                    http://www.google.com/schemas/sitemap-image/1.1/sitemap-image.xsd"></urlset>
                """
                filee.write(structure)
                filee.close()

            try:
                writeToSiteMap(errorXml, editedUrl, currentTime)
            except Exception as e:
                errorM = str(e)
                print(errorM)
                handleError(errorM)

            continue
        print("\n******************** Optimizing Images Present In Data ** ****************************************\n")

        folderName = editedUrl.split(
            "/")[-2]
        if not os.path.exists(folderName):
            os.makedirs(folderName)

        pathImage = folderName+"/"+imageUrl.split("/")[-1]

        # response
        if requests.get(imageUrl).status_code == 200:
            try:
                optimizeImage(imageUrl, "{0}".format(
                    pathImage))
            except:
                continue

        else:
            imageUrl = "https://ctdimg.ams3.digitaloceanspaces.com/blank.png"
            img_data = requests.get(imageUrl).content
            with open("downloaded.jpg", 'wb') as handler:
                handler.write(img_data)
            img = Image.open('downloaded.jpg').convert('RGB')
            img.save("{0}".format(
                pathImage), 'jpeg', optimize=True)  # quality=20

        modified_p_images_url = []
        if len(p_images_urls) != 0:
            for p_images_url in p_images_urls:
                imge_path = folderName+"/"+p_images_url.split("/")[-1]
                try:
                    optimizeImage(p_images_url, "{0}".format(imge_path))
                except:
                    continue

                modified_p_images_url.append(imageDomain +
                                             imge_path)

            r1 = re.findall(r"<img.+?/>", pTagsDiv)
            count = 0
            ind = 0
            print("modified", len(modified_p_images_url))
            print("r1", len(r1))
            for i in r1:
                # ind = int(count)
                # print(i)
                #print("findall", i)
                if 'image/gif' not in i:
                    print(i)
                    pTagsDiv = pTagsDiv.replace(
                        i, "<img src={0} class='img-fluid w-100'/>".format(modified_p_images_url[ind]))
                    ind += 1
                else:
                    pTagsDiv = pTagsDiv.replace(
                        i, "")

                # count += 0.5

            # exit()
            print("str", pTagsDiv)

        print("\n******************** Managing Some Data Before Creating HTML ** ****************************************\n")

        # Changes imageUrl, visitDomain
        editedMetas = []
        for meta in metas:
            if str(meta.get("property")) == "og:image":
                newMetaOgImg = '<meta content={0} property="og:image"/>'.format(
                    "https://ctdimg.ams3.digitaloceanspaces.com/" + pathImage)
                editedMetas.append(newMetaOgImg)
            elif str(meta.get("property")) == "og:url":
                metaContent = meta.get("content").split("/")
                newMetaOgUrl = '<meta content="{0}/{1}/" property="og:url"/>'.format(
                    visitDomain, metaContent[3])
                editedMetas.append(newMetaOgUrl)
            else:
                editedMetas.append(meta)

        filteredCategoryText = []
        filteredCategoryUrl = []

        j = urlopen(
            'https://ctdjson.ams3.digitaloceanspaces.com/categorymaster.json')
        jsonResponse = json.loads(j.read().decode())
        for url in jsonResponse["urls"]:

            if url["url"] in categoryUrlList:
                filteredCategoryUrl.append(url["url"])
                filteredCategoryText.append(url["Title"])

        if categoryUrlList:
            categoryUrlTxtZipped = zip(
                filteredCategoryText, filteredCategoryUrl)

        else:
            categoryUrlTxtZipped = ()

        print("\n******************** Creating HTML Template And Putting Data ** ****************************************\n")

        filteredTagTexts = []
        filterdTagUrl = []

        j = urlopen(
            'https://ctdjson.ams3.digitaloceanspaces.com/tagmaster.json')
        jsonResponse = json.loads(j.read().decode())
        for url in jsonResponse["urls"]:
            modUrl = visitDomain + "/tag/" + \
                url["Title"].lower() + "/".format(visitDomain)
            if url["Title"] in tagTexts:
                print("Matched", url["Title"])
                filteredTagTexts.append(url["Title"])
            if modUrl in tagUrls:
                print("Matched", modUrl)
                filterdTagUrl.append(modUrl)

        if tagTexts:
            tagUrlTxtZipped = zip(filteredTagTexts, filterdTagUrl)

        else:
            tagUrlTxtZipped = ()

        htmlTemp = createHtml(editedMetas, title, headerText, pathImage, reportedBY,
                              modified_p_images_url, pTagsDiv, tagUrlTxtZipped, categoryUrlTxtZipped, imageUrlTitle, imageUrlAlt)

        if not os.path.exists(folderName):
            os.makedirs(folderName)
        fileName = "{0}/index.html".format(folderName)
        fil = open(fileName, "w+")
        fil.write(htmlTemp)
        fil.close()

        print("\n******************** Uploading Files To Amazon Bucket ** ****************************************\n")

        htmlFolder = folderName + "/"+"index.html"

        images_path = []
        for p_images_url in p_images_urls:
            imge_path = folderName+"/"+p_images_url.split("/")[-1]
            images_path.append(imge_path)

        images_path.append(pathImage)

        try:
            uploadingToAmazon(htmlFolder, images_path)
        except Exception as e:
            errorM = str(e)
            print(errorM)
            handleError(errorM)

        try:
            shutil.rmtree(folderName)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))

        print("\n******************** Saving Current Recording In XML ** ****************************************\n")

        try:
            f = open(sitemapMain)

        except IOError:

            fil = open(sitemapMain, "w+")
            structure = """<?xml version="1.0" encoding="UTF-8"?>
            <?xml-stylesheet type="text/xsl" href="https://customstoday.com/wp-content/plugins/xml-sitemap-feed/includes/xsl/sitemap.xsl.php?ver=4.3.2"?>
            <!-- generated-on="2020-07-14T10:52:22+00:00" -->
            <!-- generator="XML & Google News Sitemap Feed plugin for WordPress" -->
            <!-- generator-url="http://status301.net/wordpress-plugins/xml-sitemap-feed/" -->
            <!-- generator-version="4.3.2" -->
            <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
                http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd
                http://www.google.com/schemas/sitemap-image/1.1
                http://www.google.com/schemas/sitemap-image/1.1/sitemap-image.xsd"></urlset>
            """
            fil.write(structure)
            fil.close()

        try:
            writeToSiteMap(sitemapMain, editedUrl, currentTime)  # sitemapMain
        except Exception as e:
            errorM = str(e)
            print(errorM)
            handleError(errorM)

        noOfRecProcessed += 1

        visitingUrl = editedUrl

        ind += 1

        try:

            js = open("forPython.json", "r")
            json.loads(js.read())
            val = {
                "xmlurl": xmlurl,
                "visitDomain": visitDomain,
                "oldDomain": oldDomain,
                "server": server,
                "k1": k1,
                "k2": k2,
                "lastdonejson": lastTimeStamp,  # theLastHtmlTimeStamp
                "sitemapMain": sitemapMain,
                "errorXml": errorXml,
            }

            js.close()

            dumpedJson = json.dumps(val)
            with open("forPython.json", "w") as p:
                p.write(dumpedJson)

        except Exception as e:
            errorM = str(e)
            print(errorM)
            handleError(errorM)

    endTime = strftime(str(today)+"T%X+00:00", gmtime())
    print("\n******************** Creating Log And Exiting ** ** ****************************************\n")
    exitProgram(endTime, xmlurl, startTime, endTime, noOfRecProcessed,
                editedFirstHtmlTimeStamp, editedtheLastHtmlTimeStamp, visitingUrl)


mainController()


def convertTxtToJson():
    arr = []
    f = open("categorymaster.txt", "r")
    for line in f:
        fields = line.strip().split(',')
        arr.append({
            "Title": fields[1],
            "url": fields[0].strip()
        })

    x = open("categorymaster.json", 'w+')
    x.write(json.dumps(arr, indent=2))


# XMl Record start , XML Record time
