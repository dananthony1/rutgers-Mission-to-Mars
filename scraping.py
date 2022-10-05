# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "last_modified": dt.datetime.now(),
      "hemispheres": scrape_hemispheres(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    
    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    #url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    #Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    return news_title, news_p


# ### JPL Space Images Featured Images


def featured_image(browser):
# Visit URL
    url = 'https://spaceimages-mars.com'
    #url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    #img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'
    return img_url

# ### Mars Facts

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
        #df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]
    except BaseException:
        return None
    
    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def scrape_hemispheres(browser):
    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemispheres = []
    hemisphere_image_urls = []
    hemisphere_image_titles = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    img_soup = soup(html, 'html.parser')
    img_item= img_soup.find_all('div', class_='item')
    for img in img_item:
    
        add = img.find('a').get('href')
        add_url = f'https://marshemispheres.com/{add}'
        browser.visit(add_url)
        html = browser.html
        img_soup = soup(html, 'html.parser')
    
        title = img_soup.find('h2').text.strip()
        hemisphere_image_titles.append(title)
    
        add2 = img_soup.find('img', class_="wide-image").get('src')
        add_url2 = f'https://marshemispheres.com/{add2}'
        browser.visit(add_url2)
        html = browser.html
        img_soup = soup(html, 'html.parser')

        img_url = img_soup.find('img').get('src')
        hemisphere_image_urls.append(img_url)

        print(img_url)
        print(title)
        print('-----------')

    for i in range(0, len(hemisphere_image_urls)):
        hemisphere = {}
        hemisphere = {'img_url': hemisphere_image_urls[i], 'title': hemisphere_image_titles[i]}
        hemispheres.append(hemisphere)

    browser.quit()

    return hemispheres

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())

