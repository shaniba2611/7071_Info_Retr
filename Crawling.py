import json
import requests
import time
import urllib.robotparser
import feedparser
import os
from bs4 import BeautifulSoup
import pandas  as pd
from Indexing import indexing


def read_crawl_delay():
    print("Polite crawling : Checking the robot.txt file")
    robotparser = urllib.robotparser.RobotFileParser()
    robotparser.set_url("https://pureportal.coventry.ac.uk/en/robots.txt")
    robotparser.read()
    return (robotparser.crawl_delay("*"))


def write_data_tojson(data):
    with open(os.path.join("data", "output.json"), "w") as data_file:
        json.dump(data, data_file)


def get_staff_details(crawler_delay):
    print("Collecting staff details in the department")
    page_count = 0
    staff_data = {"name": [], "link": []}
    staff_url = "https://pureportal.coventry.ac.uk/en/organisations/school-of-economics-finance-and-accounting/persons/"
    staff_list = []
    while True:
        time.sleep(crawler_delay)
        print(f"{staff_url}?page={page_count}")
        staff_list.append(f"{staff_url}?page={page_count}")
        staff_url_1 = staff_list.pop(0)
        all_staff = feedparser.parse(staff_url_1)
        if all_staff.entries == []:
            break
        for this_staff in all_staff.entries:
            if ('School of Economics, Finance and Accounting').lower() in (this_staff.summary).lower():
                staff_data["name"].append(this_staff.title)
                staff_data["link"].append(this_staff.link)
        page_count += 1
    print("Number of staffs in School of Economics, Finance and Accounting ", len(staff_data["name"]))

    return staff_data


def check_sefa_staff(staff_data, person_link):
    if (any(any(person_link in s for s in subList) for subList in staff_data.values())):
        return 1
    else:
        return 0


def crawling():
    doc_id = 0
    not_found_url = []
    publication_data_list = {"doc_id": [], "title": [], "link": [], "text": [], "published": [], "authors": [],
                             "content": []}
    print("Crawling function started")
    crawler_delay = read_crawl_delay()
    print("Crawler delay is:", crawler_delay)
    staff_data = get_staff_details(crawler_delay)
    print("Collected all the staff details")

    print("Collecting publications details")
    page_no = 0
    publications_link = "https://pureportal.coventry.ac.uk/en/organisations/school-of-economics-finance-and-accounting//publications/"
    page_to_visit = []
    # print("Adding page links to visit ......", end="\n\n")
    while True:
        time.sleep(crawler_delay)
        url_link = publications_link + f"?page={page_no}"
        print(url_link)
        journal_feed = feedparser.parse(url_link)
        if journal_feed.entries == []:
            break
        for journal in journal_feed.entries:
            flag = 0
            aut = []
            soup = BeautifulSoup(journal.description, "html.parser")
            authors = soup.findAll('a', class_='link person')
            for a in authors:
                if (check_sefa_staff(staff_data, a.get('href')) == 1):
                    flag = 1
                    break
            if flag == 1:
                publication_data_list["doc_id"].append(doc_id)
                publication_data_list["title"].append(journal.title)
                publication_data_list["link"].append(journal.link)
                publication_data_list["published"].append(journal.published)
                desc = soup.text
                desc = desc.replace(journal.title, "")
                desc = desc.replace('\u2212', " ")
                string_encode = desc.encode("ascii", "ignore")
                string_decode = string_encode.decode()
                publication_data_list["text"].append(string_decode)
                doc_id += 1
                for a in authors:
                    aut.append(" " + a.get('href') + " ")
                publication_data_list["authors"].append(aut)
                page_to_visit.append((journal.link))

            else:
                not_found_url.append(journal.link)
        page_no += 1
    print("Found a total of ", len(not_found_url) + len(page_to_visit), " publications and out of which ",
          len(page_to_visit), " publications have authors from School of Economics, Finance and Accounting")
    print("Reading the abstract of selected publications")

    doc_id = 0
    print("Priyanka1")
    print(page_to_visit)
    print(len(page_to_visit))

    i = 0

    # while page_to_visit != []:
    while i < len(page_to_visit):
        # print("inside while")
        url_link = page_to_visit.pop(0)
        print(page_to_visit.pop(0))
        page = requests.get(url_link)
        soup = BeautifulSoup(page.text, "html.parser")
        txt = soup.text
        txt1 = txt.replace("\n", " ")
        txt1 = txt1.replace('\u2212', " ")
        string_encode = txt1.encode("ascii", "ignore")
        string_decode = string_encode.decode()
        publication_data_list["content"].append(string_decode)
        doc_id = doc_id + 1

    write_data_tojson(publication_data_list)
    print("All the publications checked and wrote the crawled data to file")
    author_count = []
    for i in range(len(publication_data_list["doc_id"])):
        txt = publication_data_list["authors"][i]
        for j in txt:
            author_count.append(j)
    persons = {"name": [], "profile": [], "count": []}
    for j in author_count:
        t1 = j.split("/persons/", 1)[1]
        fn = t1.partition('-')[0]
        ln = t1.partition('-')[2]
        name = fn.capitalize() + " " + ln.capitalize()
        persons["name"].append(name)
        persons["profile"].append(j)
        persons["count"].append(author_count.count(j))
    p_df = pd.DataFrame(persons)
    p_df = p_df.drop_duplicates().reset_index(drop=True)
    print(p_df)

    # except:
    print("Crawling completed")
    # indexing()


if __name__ == "__main__":
    print("Main function")
    crawling()
