from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

browser = webdriver.Chrome(options=options)

def get_page_count(keyword):
  base_url = "https://kr.indeed.com/jobs?q="
  browser.get(f"{base_url}{keyword}&start=100000")
  if browser.page_source == None:
    print("ERROR!")
  else:
    soup = BeautifulSoup(browser.page_source, "html.parser")
    pagination = soup.find("nav", class_="css-jbuxu0 ecydgvn0")
    pages = pagination.find("button", {"data-testid":"pagination-page-current"})
    if pages == None:
      return 1
    count = int(pages.text)
    if count > 50:
      print(f"너무 많은 페이지가 존재하기 때문에 {count}개의 페이지중 {count//2}개의 페이지만 추출하겠습니다.")
      count = count//2
    return count
    

def extract_indeed_jobs(keyword):
  pages = get_page_count(keyword)
  print(f"found {pages} pages")
  results = []
  for page in range(pages):
    base_url = "https://kr.indeed.com/jobs"
    final_url = f"{base_url}?q={keyword}&start={page*10}"
    print(f"Requesting, {final_url}")
    browser.get(final_url)
    
    if browser.page_source == None:
      print("ERROR!")
    else:
      soup = BeautifulSoup(browser.page_source, "html.parser")
      job_list = soup.find("ul", class_="jobsearch-ResultsList css-0")
      jobs = job_list.find_all("li", recursive=False)
      for job in jobs:
        zone = job.find("div", class_="mosaic-zone")
        if zone == None:
          anchor = job.select_one("h2 a")
          title = anchor["aria-label"]
          link = anchor["href"]
          company = job.find("span", class_="companyName")
          location = job.find("div", class_="companyLocation")
          job_data = {
            "link" : f"https://kr.indeed.com{link}",
            "company" : company.string.replace(",", " "),
            "location" : location.string.replace(",", " "),
            "position" : title.replace(",", " ")
          }
          results.append(job_data)
  return results