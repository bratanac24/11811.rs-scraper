import requests, bs4, xlwt, time, re
from xlwt import Workbook

regex_phone = re.compile(r'\d{3}/\d{3}-\d{3,4}')

#res = requests.get("http://www.11811.rs/Delatnosti/Butici-i-modne-ku%C4%87e")
base_link = "http://www.11811.rs"
pagination = "/sve/"
links = []
#contact = {"name":"","address":"","phone":"","about":""}
contacts = []
test_link = "response.html"
total = 0
excel_name = input("Unesi naziv izlaznog excel fajla bez ekstenzije: ")

def init_links():
    links_file = open("starting_links.txt","r")
    global links
    links = links_file.read().splitlines()

def collect_page(link):

    #global contact
    global contacts
    """
    res = requests.get(link)
    soup = bs4.BeautifulSoup(res.text,features="html.parser")

    pages = soup.find("div",id="rezultatiPretrageVrh")
    pages = pages.find("div", id="rezultatiPretragePaginacija")
    pages = pages.find_all("a", href=True)
    #print(pages[-1]["href"])
    end = pages[-1]["href"]
    end = end.split("/")
    num_of_pages = int(end[-1])
    """
    for i in range(30):

        url = link+pagination+str(i+1)
        res = requests.get(url)
        #res = open(test_link,"rb")
        soup = bs4.BeautifulSoup(res.text,features="html.parser")

        #elements = soup.find("div", id="rezultatiPretrage")
        data = soup.find("table", id="sr-data")
        #print(elements)
        #elements = elements.find("tbody")
        try: elements = data.find_all("tr", recursive = False)
        except:continue
        #try:
        for element in elements:
            name = ""
            address = ""
            phone = ""
            about = ""    
            name = element.find("a", class_="narandzastiLinkG").text
            address_phone = element.find("div", id = "podaciIzPublikacijeRezultati")
            try: phone = regex_phone.search(address_phone.text).group()
            except: pass
            address_phone = address_phone.find_all("code")
            if len(address_phone) < 3: continue
            address = address_phone[0].text
            
            about = element.find("h2").text.strip()
            if phone == "":
                continue
            contacts.append({"name":name,"phone":phone,"address":address,"industry":about})
        #except: pass
            
        global total
        total += 1
        print("Procitana " +str(total)+" stranica.")
        time.sleep(10)
        

    print("Procitana kategorija!")

def write_to_excel():
    wb = Workbook()
    sheet1 = wb.add_sheet("Sheet1")
    
    #INIT SHEET COLUMNS
    sheet1.write(0,0,"Naziv Firme")
    sheet1.write(0,1,"Broj Telefona")
    sheet1.write(0,2,"Adresa")
    sheet1.write(0,3,"Cime se bave")
    #sheet1.write(0,4,"Broj zaposlenih")

    
    for i,contact in enumerate(contacts):
        sheet1.write(i+1,0,contact["name"])
        sheet1.write(i+1,1,contact["phone"])
        sheet1.write(i+1,2,contact["address"])
        sheet1.write(i+1,3,contact["industry"])
        #sheet1.write(i+1,4,contact["employees"])
    
    
    wb.save(excel_name+".xls")
    print("Ispisano u Fajl")


#-----------------MAIN---------------------

init_links()   
#print(links)

for link in links:
    collect_page(link)
   #except:pass
write_to_excel()
print("Gotovo!")






