# -*- coding: utf-8 -*-
from selenium.webdriver.support.ui import Select
from BeautifulSoup import BeautifulSoup

import sys
import re
import json
import hashlib
import Navigation as Nav
from pershiess import Pershiess


all_teachers = {}
all_classes = [[] for i in xrange(5)]
all_departments = {}


def print_all_classes(browser):
    # go to classes list
    Nav.perform_std(browser, "Pcl")
    find_all_departments(browser)
    
    # why like this? because i suck at character encoding o ina
    shin = "ش"
    ye = "ي"
    dal = "د"
    sin = "س"
    for dep_id in all_departments.keys():
        select = Select(browser.find_element_by_id('edDepartment'))
        # select department by department id
        select.select_by_value(dep_id)
        browser.execute_script("Save()")
        dep_page_source = browser.page_source
        idents_list = find_all_ident(dep_page_source)
        # for every class in a department:
        for ident in idents_list:
            # navigate to the class detail page
            Nav.perform(browser, 'Edit;Ident={}'.format(ident))
            # get every section of a class
            sections = get_class_info(browser.page_source)
            # extract other info of the class
            class_info = find_class_info(browser.page_source)

            # for every section of the class put class info in it's relevant day
            for section in sections:
                if str(section)[0] != "<":
                    class_location = re.search('\(([^\)]+)\)', section.encode("utf-8")).group()
                    section = fix_letters(section).encode("utf-8").replace(class_location, '')
                    class_time = section.split('-')[1]
                    class_day = section.split('-')[0]
                    data = {
                        "day": class_day,
                        "title": class_info[0].encode("utf-8"),
                        "class_loc": class_location,
                        "class_time": class_time,
                        "teacher": class_info[1],
                        "exam_date": class_info[2].encode("utf-8"),
                        "exam_time": class_info[3].encode("utf-8"),
                        "id": class_info[4].encode("utf-8"),
                        "units": class_info[5].encode("utf-8"),
                        "group": class_info[6].encode("utf-8"),
                        "capacity": class_info[7].encode("utf-8"),
                        "department": {
                            "id": dep_id,
                            "title": all_departments[dep_id],
                        }
                    }

                    # SAT
                    if class_day[0] == shin: all_classes[0].append(data)
                    # SUN
                    elif class_day[0] == ye: all_classes[1].append(data)
                    # MON
                    elif class_day[0] == dal: all_classes[2].append(data)
                    # TUE
                    elif class_day[0] == sin: all_classes[3].append(data)
                    # WED
                    else: all_classes[4].append(data)

            browser.execute_script("try{Exit();}catch(e){}")

    # save extracted data as a json file
    with open('data.json', 'w+') as outfile:
        json.dump({
            "classes": all_classes,
            "teachers": all_teachers,
            "departments": all_departments,
        }, outfile, ensure_ascii=False)


# returns list of all departments names
# fills all_departments dict with department ids and department names
def find_all_departments(browser):
    # Listing departments
    # don't extract these departments info
    exclude_list = ["0", "1005", "1006", "1103", "9901"]
    dep = browser.page_source
    dep_soup = BeautifulSoup(dep)
    dep_list = dep_soup.find(attrs={'id': 'edDepartment'}).findAll("option")

    # Departments list strings
    dep_list_strings = []
    for dep in dep_list:
        if dep["value"] in exclude_list:
            continue
        dep_soup = BeautifulSoup(dep.string)
        # key: department id, value: department name
        all_departments[dep["value"]] = fix_letters(dep.string).encode('utf-8').replace("بخش ", "")
        dep_list_strings += dep_soup
    return dep_list_strings


def find_all_ident(page_source):
    page_soup = BeautifulSoup(page_source)
    lessons_table = page_soup.find(
        attrs={'class': 'ptext', 'onclick': 'Click(event)'})
    lessons = lessons_table.findAll("tr")
    del (lessons[0 - 2])
    lessons_idents = []
    for lesson in lessons:
        try:
            ident = lesson['ident']
            lessons_idents.append(ident)
        except:
            pass
    return lessons_idents


def get_class_info(page_source):
    soup = BeautifulSoup(page_source)
    class_time = soup.find(attrs={'id': 'edTimeRoom'})
    return class_time


def find_class_info(page_source):
    info_soup = BeautifulSoup(page_source)

    class_name = info_soup.find(attrs={"id": "edName"})
    name = class_name.string

    try:
        class_teacher_info = info_soup.find(attrs={"id": "edTch"}).string.split('*')
    except Exception as e:
        # if class has no teacher yet
        class_teacher_info = ["unknown", "unknown", "unknown"]
    class_teacher = {
        "first_name": fix_letters(class_teacher_info[1]).encode('utf-8'),
        "last_name": fix_letters(class_teacher_info[0]).encode('utf-8'),
        "field": re.sub(r'\([^)]*\)', '', fix_letters(class_teacher_info[2]).encode('utf-8'))
    }
    # creating a unique id for every teacher based on first name, last name, field
    class_teacher_id_text = class_teacher["first_name"] + class_teacher["last_name"] + class_teacher["field"]
    class_teacher_id = int(hashlib.md5(class_teacher_id_text).hexdigest(), 16)
    # add teacher to the all teachers list
    all_teachers[str(class_teacher_id)[:8].encode('utf-8')] = class_teacher
    # only getting first 8 char of the id
    class_teacher["id"] = str(class_teacher_id)[:8].encode('utf-8')

    class_exam_date = info_soup.find(attrs={"id": "edFinalDate"})
    class_exam_time = info_soup.find(attrs={"id": "edFinalTime"})

    class_id = info_soup.find(attrs={"id": "edSrl"})

    class_units = info_soup.find(attrs={"id": "edTotalUnit"})

    class_group = info_soup.find(attrs={"id": "edGroup"})

    class_capacity = info_soup.find(attrs={"id": "edCapacity"})

    info = []
    info.append(fix_letters(name))
    info.append(class_teacher)
    info.append(class_exam_date.string or "")
    info.append(class_exam_time.string or "")
    info.append(class_id.string or "")
    info.append(class_units.string or "")
    info.append(class_group.string or "")
    info.append(class_capacity.string or "")
    return info

def fix_letters(text):
    return text.replace(u"ي", u"ی").replace(u"ك", u"ک")

if __name__ == "__main__":
    args = {}
    if len(sys.argv) == 3:
        print sys.argv
        args["username"] = sys.argv[1]
        args["password"] = sys.argv[2]
    else:
        args["username"] = None
        args["password"] = None

    p = Pershiess(args)
    p.start()
    browser = p.browser

    print_all_classes(browser)

    browser.close()
