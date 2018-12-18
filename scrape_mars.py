def scrape():
    # Import dependencies ----------------------------------------------------------------
    from splinter import Browser
    from bs4 import BeautifulSoup as bs
    import requests
    import time
    import pandas as pd
   

    # set up Splinter ----------------------------------------------------------------------
    executable_path = {'executable_path': 'chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)


    # 1. NASA Mars News---------------------------------------------------------------------
    ## Scrape the NASA Mars News Site (https://mars.nasa.gov/news) and collect the latest News Title and Paragraph Text
    ## Assign the text to variables to reference later

    #! can't use requests library here, because the news are rendered by js after page is load; if use requests.get, it will only return the contents before rendering

    # 1.1 Retrieve page with splinter
    url_news = "https://mars.nasa.gov/news"
    browser.visit(url_news)
    html = browser.html

    # 1.2 Get the first news from html retrieved 
    # Create BeautifulSoup object; parse with 'html.parser'
    bsoup = bs(html, 'html.parser')

    # reach the container of the first news 
    li = bsoup.find("li",class_="slide")

    news_t = li.find("div",class_="content_title").text  # title
    news_p = li.find("div",class_="article_teaser_body").text # paragraph
    news_link = url_news.replace("/news","")+li.find("div",class_="content_title").a["href"] # link to the news (added to base url)
    news_date = li.find("div",class_="list_date").text # date



    # 2. JPL Mars Space Images - Featured Image----------------------------------------------
    ## Get the current Featured Image from JPL (https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars)

    url_img = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"

    # navigate to to full-size image url with splinter
    browser.visit(url_img)
    browser.click_link_by_partial_text('FULL IMAGE')

    # ---if try to click on the more info button, directly, sometimes it returns an error "element not visible"
    # ---the only way to avoid that it to wait until the element becomes visible, which takes time
    # --- the workaround is to get the href link and visit it insteading of trying to click the link directly
    # time.sleep(30)
    # browser.click_link_by_partial_text('more info')

    href= browser.find_link_by_partial_text("more info")[0]["href"]
    browser.visit(href)

    browser.find_by_css(".main_image").click()

    # store the image url
    featured_image_url = browser.url



    # 3. Mars Weather ------------------------------------------------------------------------
    ## Visit the Mars Weather twitter account page (https://twitter.com/marswxreport?lang=en) and scrape the latest Mars weather tweet from the page 

    # 3.1 Retrieve page using requests
    url_twitter = "https://twitter.com/marswxreport?lang=en"
    html = requests.get(url_twitter).text

    # 3.2 Get the weather post from html retrieved
    bsoup = bs(html,"html.parser")

    # all tweets are under ol
    ol = bsoup.find(id="stream-items-id")

    # put tweets in lis list
    lis = ol.findAll("li")
    # use a for loop to find the first tweet with weather info (criterion: has hPa in the post)
    mars_weather = ""
    for li in lis:
        tweet = li.find("div",class_="js-tweet-text-container").p.text
        if tweet.find("hPa"):
            mars_weather = tweet
            break

            



    # 4. Mars Facts----------------------------------------------------------------------------
    ## Visit the Mars Facts webpage (https://space-facts.com/mars/) and use Pandas to scrape the table containing facts about the planet including Diameter, Mass, etc.
    # Use Pandas to convert the data to a HTML table string.
    url_fact = "https://space-facts.com/mars/"

    # use pandas to scrape tabular data from the page
    tables = pd.read_html(url_fact)
    facts = tables[0]
   
    # store data in a list of lists
    facts = facts.values.tolist()



    # 5. Mars Hemispheres-------------------------------------------------------------------------
    ## Visit the USGS Astrogeology site (https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars) to obtain high resolution images for each of Mar's hemispheres.

    # 5.1 Retrieve the html with splinter
    url_hemi = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url_hemi)
    html = browser.html

    # 5.2 Get the urls needed from the html retrieved
    bsoup = bs(html,"html.parser")

    items = bsoup.findAll("div",class_="item")

    hemisphere_image_urls=[] # initialize list
    for item in items:
        title = item.find("h3").text # title
        url = "https://astrogeology.usgs.gov/"+item.find("div",class_="description").a["href"] # get the url for picture details 
        browser.visit(url)
        img_url = browser.find_link_by_text("Sample")[0]["href"] # get the url to the full-size picture
        hemisphere_image_urls.append( {"title":title, "img_url":img_url} ) # append a dictionary to the hemisphere_image_urls list


    # store data scraped into a dictionary--------------------------------------------------------------------
    data = {
        "news":{
            "title":news_t,
            "body":news_p,
            "link":news_link,
            "date":news_date
        },
        "feature_img":featured_image_url,
        "weather":mars_weather,
        "facts":facts,
        "hemi_img":hemisphere_image_urls 
    }

    print(data) # print to console
    return data