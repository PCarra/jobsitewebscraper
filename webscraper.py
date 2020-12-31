'''
Author: Patrick Carra
Description: This is a simple webscraper I used to speed up searching for jobs on 3 of the major job sites.
             This script accepts user input for job title, location, and radius and then will format the search query for each site.
             Finally it will write the results of the job searches for each site to a document for review.
'''

import requests, re, docx
from bs4 import BeautifulSoup

#global variables
job_title = ''
job_location = ''
job_radius = ''
doc = docx.Document()
output_file = 'jobsearch.docx'

def get_results(url, tag_ID, tag_type, tag_class):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id=tag_ID)
    job_elems= results.find_all(tag_type, class_=tag_class)
    return job_elems

def format_location(site, user_input):
    if re.search(r"\s", user_input):
        if site=='Monster':
            job_title = user_input.replace(" ", "-")
        elif site=='Indeed':
            job_title = user_input.replace(" ", "+")
        elif site=='LinkedIn':
            job_title = user_input.replace(" ", "%2B")
    else:
        job_title = user_input
    return job_title

def check_for_digits(input_string):
    return bool(re.search(r'\d', input_string))

def get_input():
    global job_title
    global job_location
    global job_radius
    is_valid=False
    while(is_valid==False):
        is_valid=False
        while(is_valid==False):
            print('Enter the type of job to look for: ')
            job_title = input()
            if check_for_digits(job_title):
                print('Enter a valid job title without digits!!!\n')
                continue

            print('Enter which city you would like to search in: ')
            job_location = input()
            if check_for_digits(job_location):
                print('Enter a valid location without digits!!!\n')
                continue

            print('Enter the number of miles for the search radius: ')
            job_radius = input()
            if job_radius.isdigit()==False:
                print('Enter a radius in the form of an integer!!!\n')
                continue

            is_valid=True

get_input()
#monsterURL = 'https://www.monster.com/jobs/search/?q=CyberSecurity&where=St.-Louis'
monsterURL = '''https://www.monster.com/jobs/search/?q={title}&where={city}'''.format(title=job_title, city=format_location('Monster', job_location))

#indeedURL = 'https://www.indeed.com/jobs?q=CyberSecurity&l=St.+Louis%2C+MO&radius=50'
indeedURL = '''https://www.indeed.com/jobs?q={title}&l={city}&radius={radius}'''.format(title=job_title, city=format_location('Indeed', job_location), radius=job_radius)

#linkedinURL = 'https://www.linkedin.com/jobs/search?keywords=CyberSecurity&location=St.%2BLouis%2C%2BMissouri&distance=50&f_TP=1&redirect=false&position=1&pageNum=0'
linkedinURL = '''https://www.linkedin.com/jobs/search?keywords={title}&location={city}&distance={radius}&f_TP=1&redirect=false&position=1&pageNum=0'''.format(title=job_title, city=format_location('LinkedIn', job_location), radius=job_radius)

monster_job_elems = get_results(monsterURL, 'ResultsContainer', 'section', 'card-content')
indeed_job_elems = get_results(indeedURL, 'resultsCol', 'div', 'jobsearch-SerpJobCard')
linkedin_job_elems = get_results(linkedinURL, 'main-content', 'li', 'job-result-card')


##############Write Monster jobs to doc
doc.add_paragraph('Monster Job Search Query: ' + monsterURL)

if len(monster_job_elems)==0:
    doc.add_paragraph('No Monster Jobs found matching search criteria!\n')

for job_elem in monster_job_elems:
    title_elem = job_elem.find('h2', class_='title')
    company_elem = job_elem.find('div', class_='company')
    location_elem = job_elem.find('div', class_='location')
    elem_list = [title_elem, company_elem, location_elem]
    links = []
    for link in job_elem.find_all('a'):
        links.append(link.get('href'))

    for elem in elem_list:
        try:
            doc.add_paragraph(elem.text.strip())
        except AttributeError as error:
            continue

    for link in links:
            doc.add_paragraph(link)

    doc.add_paragraph('\n')

##############Write Indeed jobs to doc
doc.add_paragraph('Indeed Job Search Query: ' + indeedURL)

if len(indeed_job_elems)==0:
    doc.add_paragraph('No Indeed Jobs found matching search criteria!\n')

for job_elem in indeed_job_elems:
    title_elem = job_elem.find('a', class_='jobtitle')
    company_elem = job_elem.find('span', class_='company')
    location_elem = job_elem.find('div', class_='location')
    salary_elem = job_elem.find('span', class_='salaryText')
    elem_list = [title_elem, company_elem, location_elem, salary_elem]
    links = []
    for link in job_elem.find_all('a'):
        link.append(link.get('href'))

    for elem in elem_list:
        try:
            doc.add_paragraph(elem.text.strip())
        except AttributeError as error:
            continue

    for link in links:
        doc.add_paragraph(str(link))

    doc.add_paragraph('\n')


##############Write LinkedIn jobs to doc
doc.add_paragraph('LinkedIn Job Search Query: ' + linkedinURL)

if len(linkedin_job_elems)==0:
    doc.add_paragraph('No Jobs found matching search criteria!\n')

for job_elem in linkedin_job_elems:
    title_elem = job_elem.find('h3', class_='result-card__title')
    company_elem = job_elem.find('h4', class_='result-card__subtitle')
    location_elem = job_elem.find('span', class_='job-result-card__location')
    elem_list = [title_elem, company_elem, location_elem]
    links = []
    for link in job_elem.find_all('a'):
        links.append(link.get('href'))

    for elem in elem_list:
        try:
            doc.add_paragraph(elem.text.strip())
        except AttributeError as error:
            continue

    for link in links:
        doc.add_paragraph(link)
    
    doc.add_paragraph('\n')

###########Add job count to doc
jobs = len(monster_job_elems) + len(indeed_job_elems) + len(linkedin_job_elems)
doc.add_paragraph('Jobs: '+ str(jobs))
doc.save(output_file)