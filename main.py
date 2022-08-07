import requests
from bs4 import BeautifulSoup
import csv
import re
from os.path import exists
import smtplib
import ssl

job_names = []
job_dates = []
job_details = []
job_links = []
job_emails = []
job_places = []
url = "*******************"


def web_scraping():
    job_data = []

    file_exists = exists("job_info.csv")
    if file_exists:

        with open("job_info.csv", "r+", newline='', encoding="utf-8") as in_file:
            for i, row in enumerate(csv.reader(in_file)):
                if row:
                    job_data.append(row)
            last_job = job_data[1][0]
            result = requests.get(url)
            src = result.content
            soup = BeautifulSoup(src, "html.parser")
            job_name = soup.find("h1", class_="entry-title").text

            if last_job == job_name:
                pass
            else:
                request_data()

    else:
        request_data()


def request_data():
    result = requests.get(url)
    src = result.content
    soup = BeautifulSoup(src, "html.parser")
    job_name = soup.find_all("h1", class_="entry-title")
    job_date = soup.find_all("span", class_="posted-on")
    job_detail = soup.find_all("div", class_="entry-summary")
    job_link = soup.find_all("h1", class_="entry-title")

    for date in job_date:
        dates = date.find("time", class_="entry-date published updated")
        if dates is None:
            job_dates.append("no_date")
        else:
            job_dates.append(dates.text)

    for i in range(len(job_name)):
        job_names.append(job_name[i].text)
        job_details.append(job_detail[i].text.strip()[:-14])
        job_links.append(job_link[i].find("a").attrs['href'])

    for link in job_links:
        job_info = requests.get(link)
        src = job_info.content
        soup = BeautifulSoup(src, "html.parser")
        job_email = soup.find("a", attrs={"href": re.compile("^mailto:")})
        if job_email is None:
            job_emails.append("no_email")
        else:
            job_emails.append(job_email.get("href"))
        job_place = soup.find("p", {"class": "entry-tags"})
        job_places.append(job_place.text)

    with open("job_info.csv", "w", newline='', encoding="utf-8") as job_info:
        job = csv.writer(job_info)
        job.writerow(["job_name", "job_date", "job_title", "job_place", "job_email", "job_link"])
        for j in range(len(job_dates)):
            job.writerow([job_names[j], job_dates[j], job_details[j], job_places[j], job_emails[j], job_links[j]])
            if j == 0:
                new_job = [job_names[j], job_dates[j], job_details[j], job_places[j], job_emails[j], job_links[j]]
    send_email(new_job)


def send_email(data_msg):
    sender = "**********@gmail.com"
    password = "**************"
    receiver = "**************@gmail.com"
    message = f'''subject:{data_msg[0]}
{data_msg[1]}
{data_msg[2]}
{data_msg[3]}
{data_msg[4]}
{data_msg[5]}'''

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, message.encode('utf-8').strip())


if __name__ == '__main__':
    web_scraping()
