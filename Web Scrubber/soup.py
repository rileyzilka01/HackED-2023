from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from math import ceil
import asyncio
import time
import json

allCourse={}
username = ""
password = ""
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://tsqs.srv.ualberta.ca/cgi-bin/usri/usri.pl")

class proffesor:
    def __init__(self, course):
        self.course = course
        self.count= 0
        self.goals = 0
        self.goalsWeight = 0
        self.timeEfficent = 0
        self.timeEfficentWeight = 0
        self.quality = 0
        self.qualityWeight = 0
        self.knowledgeIncrease = 0
        self.knowledgeIncreaseWeight = 0
        self.motivation = 0
        self.motivationWeight = 0
        self.communication = 0
        self.communicationWeight = 0
        self.prepared = 0
        self.preparedWeight = 0
        self.respect = 0
        self.respectWeight = 0
        self.feedback = 0
        self.feedbackWeight = 0
        self.overallMed = 0
        self.overallMedWeight = 0
        self.courseQual = 0
        self.instructQual = 0
        self.teachingQual = 0
        self.overallQual = 0
        #this method is to be called to find the avgs across all courses
    def avg(self):
        self.goals = self.goalsWeight / self.count
        self.timeEfficent = self.timeEfficentWeight / self.count
        self.quality = self.qualityWeight / self.count
        self.knowledgeIncrease = self.knowledgeIncreaseWeight / self.count
        self.motivation = self.motivationWeight / self.count
        self.communication = self.communicationWeight / self.count
        self.prepared = self.preparedWeight / self.count
        self.respect = self.respectWeight / self.count
        self.feedback =  self.feedbackWeight / self.count
        self.overallMed = self.overallMedWeight / self.count
        self.courseQual = (self.timeEfficent + self.prepared + self.communication)/3
        self.instructQual = (self.goals + self.respect)/2
        self.teachingQual = (self.motivation + self.knowledgeIncrease + self.overallMed + self.feedback + self.quality)/5
        self.overallQual = self.courseQual*0.25+self.instructQual*0.1+self.teachingQual*0.65
# function used to get the prof name from webrip
def nameGet(string):
    splitted=string.split()
    NameGetflag = True
    name = splitted[0]
    incrementName = 1
    courseFirst=course.split()[0]
    while NameGetflag == True:
        if splitted[incrementName] == courseFirst:
            NameGetflag = False
            break
        name += ' ' + splitted[incrementName]
        incrementName +=1
    return name

# function takes the beartracks ccid and password and logins to the ssri archive
def login(user, password):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "ccid")))
    driver.find_element(by=By.NAME, value ="ccid").send_keys(user)
    driver.find_element(by=By.NAME, value ="pwd").send_keys(password)
    driver.find_element(by=By.NAME, value ="login").submit()
# First arg is the year of the fall term you want to search and year upper is if you want a range also uses far term
# Input year as the last
# E.g. yearlow = 2021 and no second arg will search for the 2021/2022
# E.g. yearlow = 2020 and yearupper = 2021 will search for 2020/2021 and 2021/2022
def years(yearlow,yearupper=None):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "Continue")))
    assert yearlow >= 1995
    if yearupper == None:
        value = str(yearlow-1994)
        XPATH1 = "/html/body/form/table/tbody/tr[2]/td/table[2]/tbody/tr[2]/td/table/tbody/tr[" + value + "]/td/label/input"
        driver.find_element(by= By.XPATH, value =XPATH1).click()
    else:
        assert yearupper <= 2022
        for x in range (yearupper-yearlow):
            value = str(yearlow+x-1994)
            XPATH1 = "/html/body/form/table/tbody/tr[2]/td/table[2]/tbody/tr[2]/td/table/tbody/tr[" + value + "]/td/label/input"
            driver.find_element(by= By.XPATH, value =XPATH1).click()
    driver.find_element(by = By.NAME, value = "Continue").submit()
# Searches for either a course or a prof
# First input is either the name of the prof or the course, input as string
# Second input is option if searching for the defualt of the Course Title, If choosing to Sort by Prof input as False
def CourseOrProfSearch(SearchInput,CrsBool=True):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "Execute Search")))
    clear = driver.find_element(by = By.NAME, value = "search_text").clear()
    if CrsBool == True:
        driver.find_element(by = By.NAME, value = "search_text").send_keys(SearchInput)
    elif CrsBool == False:
        driver.find_element(by = By.NAME, value = "search_text").send_keys(SearchInput)
        driver.find_element(by = By.XPATH, value = "/html/body/form/table[2]/tbody/tr[2]/td[3]/label[1]/input").click()

    driver.find_element(by = By.NAME, value = "Execute Search").submit()
# grabs the html from the current list
def dataGrabber():
    htmls=[]
    list=driver.find_element(by = By.NAME, value = "rep_list")
    searchResults = Select(list)
    option_list = searchResults.options
    listLength=len(option_list)
    totalSearches=ceil(listLength/20)
    remainder = listLength-((totalSearches-1)*20)
    for x in range(totalSearches):
        list=driver.find_element(by = By.NAME, value = "rep_list")
        searchResults = Select(list)
        searchResults.deselect_all()
        if ((remainder != 0) and (x==(totalSearches-1))):
            element = driver.find_element(by = By.NAME, value = "rep_list")
            driver.execute_script("arguments[0].size = '200'", element)
            for i in range(remainder):
                searchResults.select_by_index(i+x*20)
            driver.find_element(by=By.NAME, value ="Show Reports").submit()
            htmls.append(driver.page_source)
            driver.execute_script("window.history.go(-1)")
        else:
            element = driver.find_element(by = By.NAME, value = "rep_list")
            driver.execute_script("arguments[0].size = '200'", element)
            for i in range(20):
                searchResults.select_by_index(i+x*20)
            driver.find_element(by=By.NAME, value ="Show Reports").submit()
            htmls.append(driver.page_source)
            driver.execute_script("window.history.go(-1)")
    return(htmls, listLength)

def dataProcessor(htmlInput,count):
    totalSearches=len(htmlInput)
    remainder = count - ((totalSearches-1) * 20)
    profList=[]
    for x in range(totalSearches):
        soup = BeautifulSoup(htmlInput[x], 'html.parser')
        form=soup.body.form
        if ((remainder != 0) and (x==(totalSearches-1))):
            for i in range(remainder):  
                profFlag = False
                profObj = proffesor(course)
                namestring=form.contents[1+i*6].tbody.contents[1].td.b.string
                name = nameGet(namestring)
                if len(profList)>=1:
                    for j in range (len(profList)):
                        if profList[j]["name"] == name:
                            profObj = profList[j]["class"]
                            index=j
                            profFlag=True
                reviewsString=form.contents[1+i*6].tbody.contents[4].td.b.string
                reviews=float(reviewsString.split()[0])
                profObj.count += reviews
                goal=float(form.contents[2+i*6].tbody.contents[2].contents[12].string.strip())
                profObj.goalsWeight += reviews * goal
                timeEfficent=float(form.contents[2+i*6].tbody.contents[3].contents[12].string.strip())
                profObj.timeEfficentWeight += timeEfficent*reviews
                quality=float(form.contents[2+i*6].tbody.contents[4].contents[12].string.strip())
                profObj.qualityWeight += reviews * quality
                knowledgeIncrease=float(form.contents[2+i*6].tbody.contents[5].contents[12].string.strip())
                profObj.knowledgeIncreaseWeight += reviews * knowledgeIncrease
                motivation=float(form.contents[2+i*6].tbody.contents[6].contents[12].string.strip())
                profObj.motivationWeight += motivation * reviews
                communication=float(form.contents[2+i*6].tbody.contents[7].contents[12].string.strip())
                profObj.communicationWeight += communication * reviews
                prepared=float(form.contents[2+i*6].tbody.contents[8].contents[12].string.strip())
                profObj.preparedWeight += prepared * reviews
                respect=float(form.contents[2+i*6].tbody.contents[9].contents[12].string.strip())
                profObj.respectWeight += respect * reviews
                feedback=float(form.contents[2+i*6].tbody.contents[10].contents[12].string.strip())
                profObj.feedbackWeight += feedback * reviews
                overall=float(form.contents[2+i*6].tbody.contents[11].contents[12].string.strip())
                profObj.overallMedWeight += overall * reviews
                if profFlag == True:
                    profList[index]["class"] = profObj
                else:
                    profList.append({"name":name,"class":profObj})
                profObj=0
        else:
            for i in range(20):
                profFlag = False
                profObj = proffesor(course)
                namestring=form.contents[1+i*6].tbody.contents[1].td.b.string
                name = nameGet(namestring)
                if len(profList)>=1:
                    for j in range (len(profList)):
                        if profList[j]["name"] == name:
                            profObj = profList[j]["class"]
                            index=j
                            profFlag=True
                reviewsString=form.contents[1+i*6].tbody.contents[4].td.b.string
                reviews=float(reviewsString.split()[0])
                profObj.count += reviews
                goal=float(form.contents[2+i*6].tbody.contents[2].contents[12].string.strip())
                profObj.goalsWeight += reviews * goal
                timeEfficent=float(form.contents[2+i*6].tbody.contents[3].contents[12].string.strip())
                profObj.timeEfficentWeight += timeEfficent*reviews
                quality=float(form.contents[2+i*6].tbody.contents[4].contents[12].string.strip())
                profObj.qualityWeight += reviews * quality
                knowledgeIncrease=float(form.contents[2+i*6].tbody.contents[5].contents[12].string.strip())
                profObj.knowledgeIncreaseWeight += reviews * knowledgeIncrease
                motivation=float(form.contents[2+i*6].tbody.contents[6].contents[12].string.strip())
                profObj.motivationWeight += motivation * reviews
                communication=float(form.contents[2+i*6].tbody.contents[7].contents[12].string.strip())
                profObj.communicationWeight += communication * reviews
                prepared=float(form.contents[2+i*6].tbody.contents[8].contents[12].string.strip())
                profObj.preparedWeight += prepared * reviews
                respect=float(form.contents[2+i*6].tbody.contents[9].contents[12].string.strip())
                profObj.respectWeight += respect * reviews
                feedback=float(form.contents[2+i*6].tbody.contents[10].contents[12].string.strip())
                profObj.feedbackWeight += feedback * reviews
                overall=float(form.contents[2+i*6].tbody.contents[11].contents[12].string.strip())
                profObj.overallMedWeight += overall * reviews
                if profFlag == True:
                    profList[index]["class"] = profObj
                else:
                    profList.append({"name":name,"class":profObj})
                profObj=0
    allCourse[course]={}
    for yy in range(len(profList)):
        obj=profList[yy]["class"]
        obj.avg()
        profName=profList[yy]["name"]
        allCourse[course][profName]={}
        allCourse[course][profName]["count"]=obj.count
        allCourse[course][profName]["goals"]=obj.goals
        allCourse[course][profName]["timeEfficent"]=obj.timeEfficent
        allCourse[course][profName]["quality"]=obj.quality
        allCourse[course][profName]["knowledgeIncrease"]=obj.knowledgeIncrease
        allCourse[course][profName]["motivation"]=obj.motivation
        allCourse[course][profName]["communication"]=obj.communication
        allCourse[course][profName]["prepared"]=obj.prepared
        allCourse[course][profName]["respect"]=obj.respect
        allCourse[course][profName]["feedback"]=obj.feedback
        allCourse[course][profName]["overallMed"]=obj.overallMed
        allCourse[course][profName]["courseQual"]=obj.courseQual
        allCourse[course][profName]["instructQual"]=obj.instructQual
        allCourse[course][profName]["teachingQual"]=obj.teachingQual
        allCourse[course][profName]["overallQual"]=obj.overallQual

    return(profList)
login(username,password)
years(2000,2021)

with open('./json_data.json', 'r') as f:
        data = json.load(f)

dataSet = set()
for entry in data:
    nameSplit = entry[0]["Course"].split("-")
    dataSet.add(nameSplit[0].strip())

toDo = []
for course in dataSet:
    CourseOrProfSearch(course+" LEC")
    try:
        data,count=dataGrabber()
    except:
        driver.execute_script("window.history.go(-1)")
        continue
    try:
        final=dataProcessor(data,count)
        toDo.append(final[0])
    except:
        driver.execute_script("window.history.go(-1)")
        continue
    driver.execute_script("window.history.go(-1)")

json_object = json.dumps(allCourse, indent=4)
with open("data.json", "w") as outfile:
    outfile.write(json_object)
time.sleep(1)
    
