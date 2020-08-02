import requests, bs4, xlwt, time, re
from xlwt import Workbook
from stem import Signal
from stem.control import Controller

def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session

def renew_connection():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(password="d0nat3la")
        controller.signal(Signal.NEWNYM)

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
    session = get_tor_session()
    for i in range(30):

        url = link+pagination+str(i+1)
        try: 
            res = session.get(url)
        except:
            print("Neuspelo skidanje")
            continue
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
            person_name = ""
            name = ""
            address = ""
            phone = ""
            note = ""  
            email = ""  
            name = element.find("a", class_="narandzastiLinkG").text
            address_phone = element.find("div", id = "podaciIzPublikacijeRezultati")
            try: phone = regex_phone.search(address_phone.text).group()
            except: pass
            address_phone = address_phone.find_all("code")
            if len(address_phone) < 3: continue
            address = address_phone[0].text
            
            note = element.find("h2").text.strip()
            if phone == "":
                continue
            contacts.append({"person_name":person_name,"name":name,"phone":phone,"address":address,"email":email,"note":note})
        #except: pass
            
        global total
        total += 1
        print("Procitana " +str(total)+" stranica.")
        renew_connection()
        time.sleep(5)
        

    print("Procitana kategorija!")

def write_to_excel():
    wb = Workbook()
    sheet1 = wb.add_sheet("Sheet1")
    
    #INIT SHEET COLUMNS
    sheet1.write(0,0,"Ime i Prezime")
    sheet1.write(0,1,"Naziv Firme")
    sheet1.write(0,2,"Adresa")
    sheet1.write(0,3,"Telefon")
    sheet1.write(0,4,"E-mail")
    sheet1.write(0,5,"Note")
    
    for i,contact in enumerate(contacts):
        sheet1.write(i+1,0,contact["person_name"])
        sheet1.write(i+1,1,contact["name"])
        sheet1.write(i+1,2,contact["address"])
        sheet1.write(i+1,3,contact["phone"])
        sheet1.write(i+1,4,contact["email"])
        sheet1.write(i+1,5,contact["note"])
        #sheet1.write(i+1,4,contact["employees"])
    
    
    wb.save(excel_name+".xls")
    print("Ispisano u Fajl")

def write_to_csv():

    csv = open(excel_name+".csv","w",encoding="utf-8")
    
    #WRITTE HEADER
    csv.write("Ime i prezime,Naziv Firme,Adresa,Telefon,E-mail,Note\n")
    

    for contact in contacts:
        contact["address"].replce(",","")
        csv.write(contact["person_name"]+","+contact["name"]+","+contact["address"]+","+contact["phone"]+","+contact["email"]+","+contact["note"]+"\n")
    csv.close()

#-----------------MAIN---------------------

init_links()   
#print(links)

for link in links:
    collect_page(link)
   #except:pass
write_to_excel()
write_to_csv()
print("Gotovo!")






