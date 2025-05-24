from fpdf import FPDF
from pdf2image import convert_from_path
from kivy.uix.screenmanager import ScreenManager
from kivy.core.text import LabelBase
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.screen import MDScreen
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.button import MDFlatButton
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from kivy.utils import rgba

import os
import requests
import mimetypes

from kivy.metrics import dp
from kivymd.uix.datatables import MDDataTable

from pathlib import Path
from fpdf import FPDF
from datetime import datetime

Window.size = (310,600)

base_url = "http://localhost:5000/api/v1/ems/"
headers = {'Content-type': 'application/json'}

class PDF(FPDF):
    font_name = 'Times'
    orientation = "P"
    format = "A4"
    titlehead = "Machakos County E-Bursary Report"
    title = ""
    w=0
    def header(self):
        self.set_font(self.font_name, 'B', 20)
        self.w = self.get_string_width(self.title) + 6
        self.image('assets/logo_full.png', None,None, 100)
        self.set_x((210 - self.w) / 2)
        self.set_text_color(125,202,222)
        self.cell(self.w, 3, self.titlehead, border=0, fill=0, align='C',ln=0)
        self.set_line_width(1)
        self.ln(10)
    
    def add_table_head(self):
        self.add_page('0')        
        self.set_font(self.font_name, 'B', 15)
        self.cell(self.w, 10, self.title, border=0, fill=0,ln=2)
        self.set_font(self.font_name,'B',12)
        self.cell(15,7, 'NO', 1)
        self.cell(70,7, 'APPLICANT NAME', 1)
        self.cell(45,7, 'INSTITUTION', 1)
        self.cell(70,7, 'INSTITUTION NAME', 1)
        self.cell(45,7, 'ADM/REG NO', 1)
        self.cell(30,7, 'FORM/YEAR', 1,ln=1)
    
    def add_table_row(self,all_data):
        self.set_font(self.font_name,'',12)
        for i, data in enumerate(all_data):
            i += 1
            self.cell(15,7, str(i), 1)
            self.cell(70,7, str(data[0]), 1)
            self.cell(45,7, str(data[1]), 1)
            self.cell(70,7, str(data[2]), 1)
            self.cell(45,7, str(data[3]), 1)
            self.cell(30,7, str(data[4]), 1,ln=1)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.font_name, 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

class ApproveWindow(MDScreen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.target_table = None
        self.load_url = base_url + "load"
        self.approve_url = base_url + "approve"
        self.user_url = base_url + "user"
        
        self.status_info = {
            1:("alert-circle-outline", [255 / 256, 165 / 256, 0, 1], "Denied"),
            2:("checkbox-marked-circle", [39 / 256, 174 / 256, 96 / 256, 1],"Approved",),
            3:("checkbox-blank-circle", [39 / 256, 174 / 256, 96 / 256, 1],"Pending",),
        
        }
        self.record = ""
        
        self.records = {
            "all": {
                "columns": [
                    ("No.", dp(20)),
                    ("Applicant Names", dp(35),self.sort_alphabetically),
                    ("Gender", dp(25),self.sort_alphabetically),
                    ("Disabled", dp(25),self.sort_alphabetically),
                    ("Orphan", dp(25),self.sort_alphabetically),
                    ("Gurdian Names", dp(40),self.sort_alphabetically),
                    ("Gurdian Contacts", dp(35),self.sort_alphabetically),
                    ("Gurdian ID", dp(35),self.sort_alphabetically),
                    ("Institution Category", dp(40),self.sort_alphabetically),
                    ("Institution Name", dp(40),self.sort_alphabetically),                         
                    ("Reg No.", dp(25),self.sort_alphabetically),
                    ("Year", dp(26),self.sort_alphabetically),
                    ("Status", dp(25)),
                    
                ],
                "rows": [],
                "title": "All Applicants",
            },
            "orphans": {
                "columns": [
                    ("No.", dp(20)),
                    ("Applicant Names", dp(35),self.sort_alphabetically),
                    ("Gender", dp(25),self.sort_alphabetically),
                    ("Gurdian Names", dp(40),self.sort_alphabetically),
                    ("Gurdian Contacts", dp(35),self.sort_alphabetically),
                    ("Gurdian ID", dp(35),self.sort_alphabetically),
                    ("Institution Category", dp(40),self.sort_alphabetically),
                    ("Institution Name", dp(40),self.sort_alphabetically),                         
                    ("Reg No.", dp(25),self.sort_alphabetically),
                    ("Year", dp(26),self.sort_alphabetically),
                    ("Status", dp(25)),
                    
                ],
                "rows": [],
                "title": "Orphan Applicants",
            },
            "disabled": {
                "columns": [
                    ("No.", dp(20)),
                    ("Applicant Names", dp(35),self.sort_alphabetically),
                    ("Gender", dp(25),self.sort_alphabetically),
                    ("Gurdian Names", dp(40),self.sort_alphabetically),
                    ("Gurdian Contacts", dp(35),self.sort_alphabetically),
                    ("Gurdian ID", dp(35),self.sort_alphabetically),
                    ("Institution Category", dp(40),self.sort_alphabetically),
                    ("Institution Name", dp(40),self.sort_alphabetically),                         
                    ("Reg No.", dp(25),self.sort_alphabetically),
                    ("Year", dp(26),self.sort_alphabetically),
                    ("Status", dp(25)),
                ],
                "rows": [],
                "title": "Disabled Applicant",
            },
            "university": {
                "columns": [
                    ("No.", dp(20)),
                    ("Applicant Names", dp(35),self.sort_alphabetically),
                    ("Gender", dp(25),self.sort_alphabetically),
                    ("Disabled", dp(25),self.sort_alphabetically),
                    ("Orphan", dp(25),self.sort_alphabetically),
                    ("Gurdian Names", dp(40),self.sort_alphabetically),
                    ("Gurdian Contacts", dp(35),self.sort_alphabetically),
                    ("Gurdian ID", dp(35),self.sort_alphabetically),
                    ("Institution Category", dp(40),self.sort_alphabetically),
                    ("Institution Name", dp(40),self.sort_alphabetically),                         
                    ("Reg No.", dp(25),self.sort_alphabetically),
                    ("Year", dp(26),self.sort_alphabetically),
                    ("Status", dp(25)),
                ],
                "rows": [],
                "title": "University Applicant ",
            },
            "college": {
                "columns": [
                    ("No.", dp(20)),
                    ("Applicant Names", dp(35),self.sort_alphabetically),
                    ("Gender", dp(25),self.sort_alphabetically),
                    ("Disabled", dp(25),self.sort_alphabetically),
                    ("Orphan", dp(25),self.sort_alphabetically),
                    ("Gurdian Names", dp(40),self.sort_alphabetically),
                    ("Gurdian Contacts", dp(35),self.sort_alphabetically),
                    ("Gurdian ID", dp(35),self.sort_alphabetically),
                    ("Institution Category", dp(40),self.sort_alphabetically),
                    ("Institution Name", dp(40),self.sort_alphabetically),                         
                    ("Reg No.", dp(25),self.sort_alphabetically),
                    ("Year", dp(26),self.sort_alphabetically),
                    ("Status", dp(25)),
                ],
                "rows": [],
                "title": "College Applicants",
            },
            "technical": {
                "columns": [
                    ("No.", dp(20)),
                    ("Applicant Names", dp(35),self.sort_alphabetically),
                    ("Gender", dp(25),self.sort_alphabetically),
                    ("Disabled", dp(25),self.sort_alphabetically),
                    ("Orphan", dp(25),self.sort_alphabetically),
                    ("Gurdian Names", dp(40),self.sort_alphabetically),
                    ("Gurdian Contacts", dp(35),self.sort_alphabetically),
                    ("Gurdian ID", dp(35),self.sort_alphabetically),
                    ("Institution Category", dp(40),self.sort_alphabetically),
                    ("Institution Name", dp(40),self.sort_alphabetically),                         
                    ("Reg No.", dp(25),self.sort_alphabetically),
                    ("Year", dp(26),self.sort_alphabetically),
                    ("Status", dp(25)),
                ],
                "rows": [],
                "title": "Technical Applicants",
            },
            "secondary": {
                "columns": [
                    ("No.", dp(20)),
                    ("Applicant Names", dp(35),self.sort_alphabetically),
                    ("Gender", dp(25),self.sort_alphabetically),
                    ("Disabled", dp(25),self.sort_alphabetically),
                    ("Orphan", dp(25),self.sort_alphabetically),
                    ("Gurdian Names", dp(40),self.sort_alphabetically),
                    ("Gurdian Contacts", dp(35),self.sort_alphabetically),
                    ("Gurdian ID", dp(35),self.sort_alphabetically),
                    ("Institution Category", dp(40),self.sort_alphabetically),
                    ("Institution Name", dp(40),self.sort_alphabetically),                         
                    ("Adm No.", dp(35),self.sort_alphabetically),
                    ("Form", dp(30),self.sort_alphabetically),
                    ("Status", dp(25)),
                ],
                "rows": [],
                "title": "Secondary Applicants",
            },
        }
    
    def preview(self):
        selected = self.target_table.get_row_checks()
        if len(selected) != 1:
            self.app.alert(text="Select single record!")
            return
        data = selected[0]

        fullname = data[1].split(" ")
        req_data = {
            "surname":fullname[0],
            "firstname":fullname[1],
            "institution_category":data[-5],
            "institution_name":data[-4],
            "reg":data[-3],
            "reqmail": self.app.reqmail,
        }

        req_data = str(req_data).replace("'",'"')
        resp = requests.post(self.user_url,req_data,headers=headers)
        
        if resp.status_code != 200 or not resp.json().get("id_"):
            self.app.alert(text="Unable to process request")
            return

        id_ = resp.json()["id_"]

        confirm = self.manager.get_screen("confirm")
        confirm.target_id = id_

        self.manager.transition.direction = "left"
        self.manager.current = "confirm"
        
    def on_button_press(self, instance_button):
        if not self.target_table: return
        try:
            {
                "Award": self.award,
                "Deny": self.deny,
            }[instance_button.text]()
        except KeyError:
            pass

    def on_row_press(self, instance_table, instance_row):
        if instance_row.ids.check.state == 'normal':
            instance_row.ids.check.state = 'down'
        else:            
            instance_row.ids.check.state = 'normal'

    def update_selected(self,selected,award=True):
        updating_records = []

        for data in selected:
            fullname = data[1].split(" ")
            
            data = {
                "surname":fullname[0],
                "firstname":fullname[1],
                "institution_category":data[-5],
                "institution_name":data[-4],
                "reg":data[-3],
                "reqmail": self.app.reqmail,
                "status": "2" if award else "1"
            }

            updating_records.append(data)

        
        for data in updating_records:
            data = str(data).replace("'",'"')
            requests.patch(self.approve_url,data,headers=headers)
          
        self.update_view()
        
    def award(self):
        try:
            selected = self.target_table.get_row_checks()
            self.update_selected(selected)
        except:
            return
    
    def deny(self):
        try:
            selected = self.target_table.get_row_checks()
            self.update_selected(selected,award=False)
        except:
            return

    def search(self,instance):
        if not self.target_table or not self.record: return
        search = instance.text
        if search.lower() == "":
            self.generate_table(self.record)
            return
        unsorted_data = self.target_table.row_data
        sorted_data = []
        for data in unsorted_data:
            lowercase_data = [str(x).lower() for x in data]
            if search.lower() in lowercase_data: sorted_data.append(data)
            if search.lower() in [str(x).lower() for x in list(data[-1])]: sorted_data.append(data)
        title = self.ids.rec_title.text
        column = self.records[self.record]["columns"]
        self.create_datatable(title=title,column=column,row=sorted_data)
        

    def update_view(self):
        try:
            self.load_records()
            self.generate_table(record="all")
        except:
            return

    def go_home(self):
        self.manager.transition.direction = "right"
        self.manager.current = "home"
    
    def generate_report(self):
        self.load_records()
        all_records = self.records["all"]["rows"]
        awrd_data = [(all_data[1],all_data[8],all_data[9],all_data[10],all_data[11]) for all_data in all_records if int(all_data[12][0]) == 2]
        non_awrd_data = [(all_data[1],all_data[8],all_data[9],all_data[10],all_data[11]) for all_data in all_records if int(all_data[12][0]) != 2]
        
        all_data = {
            "beneficiaries":[awrd_data, "Beneficiaries"],
            "non-beneficiaries":[non_awrd_data,"Non-Beneficiaries"],
        }
        
        for name,data in all_data.items():
            now = datetime.now()
            date_time_str = now.strftime("%Y-%m-%d_%H:%M:%S")
            
            pdf = PDF()
            pdf.title = data[1]
            pdf.add_table_head()
            pdf.add_table_row(data[0])
            pdf.output(os.path.join("reports",f'{name}_{date_time_str}.pdf'), 'F')
        self.app.alert(text="Reports generated...")
        
    def on_kv_post(self,dt):
        data_tables = MDDataTable(
            size_hint=(0.97, 0.55),
            use_pagination=True,
            column_data=[],
            row_data=[],
            check=True,
        )
        self.ids.table.add_widget(data_tables)
    
    def load_records(self):
        info = {"reqmail": self.app.reqmail}
        info = str(info).replace("'",'"')
        response = requests.post(self.load_url,info,headers=headers)
        
        data = response.json()
        if response.status_code != 200: return self.app.alert(text=data["message"])
        def sort_full(data):
            all_row = []
            
            for i,all_data in enumerate(data):
                id = i + 1
                fullname = f"{all_data['surname']} {all_data['firstname']} {all_data['othernames']}"
                gender = all_data['gender']
                disabled = all_data['is_disabled']
                orphan = all_data['is_orphan']
                g_name = all_data['parent_name']
                g_tell = all_data['parent_phone']
                g_id = all_data['parent_id']
                inst_cat = all_data['institution_category']
                inst_name = all_data['institution_name']
                form = all_data['study_year']
                reg = all_data['reg']
                status_val = int(float(all_data['status']))
                status_line = self.status_info[status_val] if self.status_info.get(status_val) else self.status_info[3]
                status = (status_val,status_line)
                all_row.append([id,fullname,gender,disabled,orphan,g_name,g_tell,g_id,inst_cat,inst_name,reg,form,status])
            return all_row

        def sort_partial(data):
            partial_row = []
            for i,partial_data in enumerate(data):
                id = i + 1
                fullname = f"{partial_data['surname']} {partial_data['firstname']} {partial_data['othernames']}"
                gender = partial_data['gender']
                g_name = partial_data['parent_name']
                g_tell = partial_data['parent_phone']
                g_id = partial_data['parent_id']
                inst_cat = partial_data['institution_category']
                inst_name = partial_data['institution_name']
                form = partial_data['study_year']
                reg = partial_data['reg']
                status_val = partial_data['status']
                status_line = self.status_info[status_val] if self.status_info.get(status_val) else self.status_info[3]
                status = (status_val,status_line)
                partial_row.append([id,fullname,gender,g_name,g_tell,g_id,inst_cat,inst_name,reg,form,status])
            return partial_row
            
        # all
        self.records["all"]["rows"] = sort_full([d for d in data])
        
        # orphans
        orphans = [d for d in data if d["is_orphan"].lower() == "yes"]
        self.records["orphans"]["rows"] = sort_partial(orphans)
        
        # disabled
        disabled = [d for d in data if d["is_disabled"].lower() == "yes"]
        self.records["disabled"]["rows"] = sort_partial(disabled)
        
        # university
        university = [d for d in data if d["institution_category"].lower() == "university"]
        self.records["university"]["rows"] = sort_full(university)
        
        # college
        college = [d for d in data if d["institution_category"].lower()  == "college"]
        self.records["college"]["rows"] = sort_full(college)
        
        # technical
        technical = [d for d in data if d["institution_category"].lower()  == "technical"]
        self.records["technical"]["rows"] = sort_full(technical)
        
        # secondary
        secondary = [d for d in data if d["institution_category"].lower()  == "secondary"]
        self.records["secondary"]["rows"] = sort_full(secondary)
    
    def sort_alphabetically(self, data):
        return zip(
            *sorted(
                enumerate(data),
                key=lambda l: l[1][-1]
            )
        )

    def create_datatable(self,title="",column=[],row=[]):
        self.ids.rec_title.text = title

        self.ids.table.clear_widgets()
        data_tables = MDDataTable(
            size_hint=(0.97, 0.55),
            use_pagination=True,
            pagination_menu_pos="auto",
            pagination_menu_height=dp(240),
            column_data=column,
            row_data=row,
            check=True,
        )
        self.target_table = data_tables
        self.ids.table.add_widget(data_tables)

    def generate_table(self,record=None):
        self.record = record
        data = self.records[record]
        column = data["columns"]
        _rows_ = data["rows"]
        row = []
        for _row_ in _rows_:
            status = _row_[-1]
            _row_.pop(-1)
            _row_.append(status[1])
            row.append(_row_)
        title = data["title"]
        
        try:
            self.create_datatable(title,column,row)
        except:
            return

class UpdateManager(MDScreen):
    update_url = base_url+"update"
    def update(self):
        username = self.ids.username.text
        email = self.ids.email.text
        passwd = self.ids.passwd.text
        confpass = self.ids.confpasswd.text
        
        if passwd != confpass:
            self.app.alert(text = "Passwords didn't match!")
            return
        
        data = {
            "username": username,
            "email": email,
            "passwd": passwd,
            "reqmail": self.app.reqmail,
        }

        data = str(data).replace("'",'"')

        try:
            response = requests.patch(self.update_url,data,headers=headers)
            data = response.json()
            
            if response.status_code != 201: 
                self.app.alert(text=data["message"])
                return
            else:
                home = self.manager.get_screen("home")
                if username != "":
                    home.ids.username.text = username
                    home.ids.drawerhead.title = username
                if email != "":
                    home.ids.email.text = email
                    home.ids.drawerhead.text = email
                

                self.app.alert(text="Details updated successful")
                self.manager.transition.direction = "right"
                self.manager.current = "home"
        except:
            self.app.alert(text="Updating details Failed")
            return
        finally:
            self.ids.username.text = ""
            self.ids.email.text = ""
            self.ids.passwd.text = ""
            self.ids.confpasswd.text = ""
    
class ForgotManager(MDScreen):
    forgot_url = base_url + "forgot"
    def forgot(self):
        email = self.ids.email.text
        passwd = self.ids.passwd.text
        confpass = self.ids.confpasswd.text
        
        for x in [email,passwd,confpass]:
            if x == None or x == "":
                self.app.alert(text = "Fields marked * are required")
                return
        if passwd != confpass:
            self.app.alert(text = "Passwords didn't match!")
            return
        
        data = {
            "reqmail": email,
            "passwd": passwd,
        }

        data = str(data).replace("'",'"')

        try:
            response = requests.patch(self.forgot_url,data,headers=headers)
            data = response.json()
            
            if response.status_code != 201: 
                self.app.alert(text=data["message"])
                return
            else:
                self.app.alert(text="Updated password successful")
                self.manager.transition.direction = "right"
                self.manager.current = "signin"
        except:
            self.app.alert(text="Password Update Failed")
            return
        finally:
            self.ids.email.text = ""
            self.ids.passwd.text = ""
            self.ids.confpasswd.text = ""
        
class RegisterManager(MDScreen):
    reg_url = base_url+"register"
    def register(self):
        username = self.ids.username.text
        email = self.ids.email.text
        passwd = self.ids.passwd.text
        confpass = self.ids.confpasswd.text
        
        for x in [username, email,passwd,confpass]:
            if x == None or x == "":
                self.app.alert(text = "Fields marked * are required")
                return
        
        if passwd != confpass:
            self.app.alert(text = "Passwords didn't match!")
            return
        
        data = {
            "username": username,
            "email": email,
            "passwd": passwd,
        }

        data = str(data).replace("'",'"')

        try:
            response = requests.put(self.reg_url,data,headers=headers)
            data = response.json()
            
            if response.status_code != 201: 
                self.app.alert(text=data["message"])
                return
            else:
                self.app.alert(text="Registration successful")
                self.manager.transition.direction = "right"
                self.manager.current = "signin"
        except:
            self.app.alert(text="Registration Failed")
            return
        finally:
            self.ids.username.text = ""
            self.ids.email.text = ""
            self.ids.passwd.text = ""
            self.ids.confpasswd.text = ""
        
class LoginManager(MDScreen):
    log_url = base_url+"login"
    def login(self):
        email = self.ids.email.text
        passwd = self.ids.passwd.text
        
        for x in [email,passwd]:
            if x == None or x == "":
                self.app.alert(text = "Email or Password missing")
                return
        
        data = {
            "email": email,
            "passwd": passwd,
        }
        data = str(data).replace("'",'"')
        try:
            response = requests.post(self.log_url,data,headers=headers)
            data = response.json()

            if response.status_code != 200: 
                self.app.alert(text=data["message"])
                return
            else:
                
                home = self.manager.get_screen("home")
                home.ids.username.text = data["username"]
                home.ids.drawerhead.title = data["username"]
                home.ids.email.text = data["email"]
                home.ids.drawerhead.text = data["email"]
                
                priv_user_id = data["priv"]
                user_priv, user_id = priv_user_id.split("::")

                self.app.user_id = int(user_id)

                self.app.reqmail = data["email"]
                self.app.is_admin = False if user_priv == "user" else True
                
                approvebtn = home.ids.approvebtn
                applybtn = home.ids.applybtn
                
                self.app.hide_widget(approvebtn,dohide=True)
                self.app.hide_widget(applybtn,dohide=True)

                if self.app.is_admin:
                    home.ids.status.text = "You are the admin"
                    self.app.hide_widget(approvebtn,dohide=False)
                else:
                    self.app.hide_widget(applybtn,dohide=False)
                    home.ids.status.text = self.app.application_status[data["status"]]
                    if data["status"] != -1: applybtn.disabled = True
                    
                
                self.app.alert(text="Login successful")
                self.manager.transition.direction = "left"
                self.manager.current = "home"
        except:
            self.app.alert(text="Login Failed")
            return
        finally:
            self.ids.email.text = ""
            self.ids.passwd.text = ""
            
        

    def show_password(self,checkbox,value):
        text = "Show password"
        hide = True
        if value:
            text = "Hide password"
            hide = False

        self.ids.passwd_text.text = text
        self.ids.passwd.password = hide

class MainWindow(MDScreen):
    def load_all(self):
        approve = self.manager.get_screen("approve")
        approve.load_records()
        if len(approve.records["all"]["rows"]) <= 0: return self.app.alert(text="No application submitted")
        approve.generate_table("all")
        self.manager.transition.direction = "left"
        self.manager.current = "approve"                

class CustomSnackbar(Snackbar):
    text = StringProperty(None)
    icon = StringProperty(None)
    font_size = NumericProperty("15sp")
 
class ApplicationPage(MDScreen):
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        
        self.apply_url = base_url+"apply"
        self.upload_url = base_url+"upload"
        self.status_url = base_url+"status"
        
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            #preview=True,
        )
        
        self.field = NumericProperty()
        self.required_fields = {
            "bank": False,
            "death": False
        }

        self.data = {
            "surname": "",
            "firstname": "",
            "othernames": "",
            "gender": "",
            "parent_name": "",
            "parent_phone": "",
            "parent_id": "",
            "is_orphan": "",
            "is_disabled": "",
            "institution_category": "",
            "institution_name": "",
            "reg": "",
            "study_year": "",
            "student_id": "",
            "fee": "",
            "bank": "",
            "death": "",
            "result": "",
        }

        self.is_orphan = False
        self.is_disabled = False
    
    def go_home(self):
        self.manager.transition.direction = "right"
        self.manager.current = "home"
                
    def check_size(self,path):
        file_stats = os.stat(path)
        size = file_stats.st_size / (1024 * 1024)
        
        if size > 12.0 : return False
        return True
        
    def check_filetype(self,file):
        filetype = mimetypes.guess_type(file)
        if filetype:
            if 'application/pdf' in filetype:
                return True, file
        
        return False, file
    
    def selected(self,selection):
        if not selection: return
        verified , path = self.check_filetype(selection)
        if not verified:
            self.app.alert(text="Invalid file type! PDF only!")
            return
        passed = self.check_size(path)
        if not passed:
            self.app.alert(text="File size over 12MB!")
            return
        
        if self.field == 1:
            self.ids.sid.text = path
            sid = self.ids.sid_preview
            self.app.hide_widget(sid,dohide=False)
            
        if self.field == 2:
            self.ids.fee.text = path
            fee = self.ids.fee_preview
            self.app.hide_widget(fee,dohide=False)
            
        if self.field == 3:
            self.ids.result.text = path
            result = self.ids.result_preview
            self.app.hide_widget(result,dohide=False)
            
        if self.field == 4:
            self.ids.bank.text = path
            bank = self.ids.bank_preview
            self.app.hide_widget(bank,dohide=False)
            
        if self.field == 5:
            self.ids.death.text = path
            death = self.ids.death_preview
            self.app.hide_widget(death,dohide=False)
    
    def file_manager_open(self,field):
        self.field = field
        self.file_manager.show(os.getcwd())
        self.manager_open = True
        
    def select_path(self, path):
        self.exit_manager()
        self.selected(path)
    
    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()
   
    def confirm_personal_details(self):
        surname = self.ids.surname.text
        firstname = self.ids.firstname.text
        othernames = self.ids.othernames.text

        for x in [surname, firstname]:
            if x == "" or x == None: 
                self.app.alert(text="fields marked * are required")
                return
        gender = self.app.selected_gender
        
        if not gender["male"] and not gender["female"]:
            self.app.alert(text="fields marked * are required")
            return
        
        
        
        male = None
        female = None
        for k,v in gender.items():
            if k == "male": male = v
            if k == "female": female = v
       
        if not male and not female:
            self.app.alert(text="fields marked * are required")
            return
        
        self.data["surname"] = surname if surname else ""
        self.data["firstname"] = firstname if firstname else ""
        self.data["othernames"] = othernames if othernames else ""

        if male:
            self.data["gender"] = "male"
        
        if female:
            self.data["gender"] = "female"
            
        self.ids.progress1.value = 100
        self.ids.num1.icon = "check-decagram"
        self.ids.carousel.load_next(mode="next")

    def select_orphan(self,instance,value):
        self.is_orphan = False
        if value: self.is_orphan = True

    def select_disabled(self,instance,value):
        self.is_disabled = False
        if value: self.is_disabled = True
     
    def show_confirmation_dialog(self):
        if self.app.dialog: 
            self.app.dialog.dismiss(force=True)
            self.app.dialog = None
        if not self.app.dialog:
            
            self.app.dialog = MDDialog()
            self.app.dialog.title="Institutions"
            self.app.dialog.type="confirmation"
            self.app.dialog.items = (
                ItemConfirm(text="University",category="university", is_dialog=True),
                ItemConfirm(text="College",category="college", is_dialog=True),
                ItemConfirm(text="TVET",category="technical", is_dialog=True),
                ItemConfirm(text="Secondary",category="secondary", is_dialog=True),
            )
           
            self.app.dialog.create_buttons()
            self.app.dialog.create_items()
            self.app.dialog.open()

    def confirm_other_details(self):
        parent_name = self.ids.parent_name.text
        parent_phone = self.ids.parent_phone.text
        parent_id = self.ids.parent_id.text
        
        for x in [parent_name, parent_phone, parent_id]:
            if x == "" or x == None: 
                self.app.alert(text="fields marked * are required")
                return
        
        self.data["parent_name"] = parent_name
        self.data["parent_phone"] = parent_phone
        self.data["parent_id"] = parent_id
        
        
        self.data["is_orphan"] = "Yes" if self.is_orphan else "No"
        self.data["is_disabled"] = "Yes" if self.is_disabled else "No"

        self.ids.progress2.value = 100
        self.ids.num2.icon = "check-decagram"
        self.ids.carousel.load_next(mode="next")

    def confirm_academic_details(self):
        institution_category = self.ids.instcat.text
        institution_name = self.ids.instname.text
        study_year = self.ids.curyear.text
        adm_no = self.ids.admno.text

        for x in [institution_category, institution_name, study_year]:
            if x == "" or x == None: 
                self.app.alert(text="fields marked * are required")
                return
        
        self.data["institution_category"] = institution_category
        self.data["institution_name"] = institution_name
        self.data["study_year"] = study_year
        self.data["reg"] = adm_no


        if self.is_orphan: 
            self.ids.death.hint_text = "*"
            self.ids.btndeath.disabled = False
            self.required_fields["death"] = True
        if self.data["institution_category"].lower() != "secondary": 
            self.ids.bank.hint_text = "*"
            self.ids.btnbank.disabled = False
            self.required_fields["bank"] = True
        else:
            self.ids.bank.hint_text = ""
            self.ids.btnbank.disabled = True
            self.required_fields["bank"] = False
        

        self.ids.progress3.value = 100
        self.ids.num3.icon = "check-decagram"
        self.ids.carousel.load_next(mode="next")

    def submit(self):
        student_id = self.ids.sid.text
        fee = self.ids.fee.text
        bank = self.ids.bank.text
        death = self.ids.death.text
        result = self.ids.result.text

        required = [fee,student_id]

        for k,v in self.required_fields.items():
            if k == "bank" and v: required.append(bank)
            if k == "death" and v: required.append(death)
        
        for x in required:
            if x == "" or x == None: 
                self.app.alert(text="fields marked * are required")
                return
        
        self.data["student_id"] = student_id
        self.data["fee"] = fee
        self.data["bank"] = bank
        self.data["death"] = death
        self.data["result"] = result
            
        self.ids.num4.icon = "check-decagram"

        self.app.alert("Application submited! Wait for processing!")

        self.apply()
        
        self.manager.transition.direction = "right"
        self.manager.current = "home"

    def preview(self,file,category="Nothing to preview"):
        self.app.alert("Please wait...")
        prev = self.manager.get_screen("preview")
        prev.document = file
        prev.preview()
        
        prev.ids.current_view.text = category
        
        self.manager.transition.direction = "left"
        self.manager.current = "preview"
        
    def process_application(self):
        pass

    def previous1(self):
        self.ids.progress1.value = 0
        self.ids.num1.icon = "numeric-1-circle"
        self.ids.carousel.load_next(mode="prev")

    def previous2(self):
        self.ids.progress2.value = 0
        self.ids.num2.icon = "numeric-2-circle"
        self.ids.carousel.load_next(mode="prev")

    def previous3(self):
        self.ids.progress3.value = 0
        self.ids.num3.icon = "numeric-3-circle"
        self.ids.carousel.load_next(mode="prev")
   
    def apply(self):
        uploads = {}
        info = {}
        
        uploadKeys = ["student_id","fee","bank","death","result"]
        for key, value in self.data.items():
            if key in uploadKeys:
                if value != "":
                    uploads[key] = (f"{key}-{self.app.user_id}.pdf", open(value,"rb"))
            else:
                info[key] = value
        
        info["reqmail"] = self.app.reqmail
        info = str(info).replace("'",'"')
        
        home = self.manager.get_screen("home")
        status = {}
        status["reqmail"]= self.app.reqmail
        response = requests.put(self.apply_url,info,headers=headers)
        data = response.json()
        if response.status_code != 201: 
            status['status'] = '5'
            status = str(status).replace("'",'"')
            response = requests.post(self.status_url,status,headers=headers)
            home.ids.status.text = self.app.application_status[5]
            return
        
        try:
            requests.put(self.upload_url,files=uploads)
        except:
            pass
        status['status'] = '1'
        status = str(status).replace("'",'"')
        response = requests.post(self.status_url,status,headers=headers)
        print(response.json())
        home.ids.status.text = self.app.application_status[1]
        
        return
  
class ItemConfirm(OneLineAvatarIconListItem):
    dialog = ObjectProperty()

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.divider = None

    def set_icon(self, instance_check):
        instance_check.active = True
        check_list = instance_check.get_widgets(instance_check.group)
        for check in check_list:
            if check != instance_check:
                check.active = False
            
class CarouselImage(MDFloatLayout):
    img_source = StringProperty()

class ConfirmScreen(MDScreen):
    document = None
    target_id = 0

    def clear_carousel(self):
        carousel = self.ids.carousel
        for wid in carousel.children:
            carousel.remove_widget(wid)

    def prepare_document(self,category):
        self.clear_carousel()
        documents = {
            "bank": (f".uploads/bank-{self.target_id}.pdf","Bank Card"),
            "student_id": (f".uploads/student_id-{self.target_id}.pdf","Student/Gurdian ID"),
            "fee": (f".uploads/fee-{self.target_id}.pdf","Fee Structure"),
            "death": (f".uploads/death-{self.target_id}.pdf","Death Certificate"),
            "result": (f".uploads/result-{self.target_id}.pdf","Results Slip"),
        }
        file,title = documents[category]

        if not os.path.exists(file):
            self.app.alert(text="File missing!")
            return
        self.ids.current_view.text = title
        self.document = file

    def show_confirmation_dialog(self):

        if self.app.dialog: 
            self.app.dialog.dismiss(force=True)
            self.app.dialog = None
        if not self.app.dialog:
            
            self.app.dialog = MDDialog()
            self.app.dialog.title="Records"
            self.app.dialog.type="confirmation"
            self.app.dialog.items = (
                ItemConfirm(text="Bank Card",category="bank", is_dialog=True),
                ItemConfirm(text="Fee Structure",category="fee", is_dialog=True),
                ItemConfirm(text="Result Slip",category="result", is_dialog=True),
                ItemConfirm(text="ID Card",category="student_id", is_dialog=True),
                ItemConfirm(text="Death Certificate",category="death", is_dialog=True),
            )
           
            self.app.dialog.create_buttons()
            self.app.dialog.create_items()
            self.app.dialog.open()

    def move_back(self):
        self.manager.transition.direction = "right"
        self.manager.current="approve"

    def preview(self):
        if not self.document or self.document == "":
            self.app.alert(text="Unable to preview file")
            return
        indexes = self.generate_preview()
        for i in range(indexes):
            self.ids.carousel.add_widget(
                CarouselImage(
                    img_source = f".tmp-uploads/image_{i}.png"
                )
            )

    def generate_preview(self):
        if not self.document: return
        
        tempdir = ".tmp-uploads/"
        for file in [os.path.join(tempdir,x) for x in os.listdir(tempdir)]:
            if file: os.remove(file)
        images = convert_from_path(self.document)

        for i in range(len(images)):
            images[i].save(f".tmp-uploads/image_{i}.png","PNG")
        return len(images)

    def previous(self):
        self.ids.carousel.load_previous()

    def next(self):
        self.ids.carousel.load_next(mode="next")
    
    def zoom(self,action="in"):
        for current in self.ids.carousel.children:
            if action.lower() == "in":
                current.size = current.size[0]+5.0, current.size[1] + 5.0
            elif action.lower() == "out":
                current.size = current.size[0]-5.0, current.size[1] - 5.0


class PreviewScreen(MDScreen):
    document = StringProperty()
    
    def move_back(self):
        self.manager.transition.direction = "right"
        self.manager.current="apply"
    
    def generate_preview(self):
        if not self.document: return
        
        tempdir = ".tmp/"
        for file in [os.path.join(tempdir,x) for x in os.listdir(tempdir)]:
            if file: os.remove(file)
        images = convert_from_path(self.document)

        for i in range(len(images)):
            images[i].save(f".tmp/image_{i}.png","PNG")
        return len(images)
        
    
    def preview(self):
        if not self.document and self.document == "":
            self.app.alert(text="Unable to preview file")
            self.manager.transition.direction = "right"
            self.manager.current = "apply"
            return
        indexes = self.generate_preview()
        for i in range(indexes):
            self.ids.carousel.add_widget(
                CarouselImage(
                    img_source = f".tmp/image_{i}.png"
                )
            )
        
    def previous(self):
        self.ids.carousel.load_previous()

    def next(self):
        self.ids.carousel.load_next(mode="next")
    
    def zoom(self,action="in"):
        for current in self.ids.carousel.children:
            if action.lower() == "in":
                current.size = current.size[0]+5.0, current.size[1] + 5.0
            elif action.lower() == "out":
                current.size = current.size[0]-5.0, current.size[1] - 5.0

class EMSApp(MDApp):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.title = "ems user interface"
        
        self.application_status = {
            -1: "No application found",
            1: "Application Submitted",
            2: "Application Verified",
            3: "Bursary Awarded",
            4: "Bursary Not Awarded",
            5: "Application Submission Failed"
        }
        self.selected_gender = {
            "male": False,
            "female": False,
        }
        self.dialog = None
        
        self.reqmail = ""
        self.is_admin = False
        self.user_id = 0

        self.selected_institution = {
            "university": False,
            "college": False,
            "technical": False,
            "secondary": False,
        }
        self.screen_manager = ScreenManager()
    
    def hide_widget(self, wid, dohide=True):
        if hasattr(wid, 'saved_attrs'):
            if not dohide:
                wid.height, wid.size_hint_y, wid.opacity, wid.disabled = wid.saved_attrs
                del wid.saved_attrs
        elif dohide:
            wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled
            wid.height, wid.size_hint_y, wid.opacity, wid.disabled = 0, None, 0, True

    
    def set_selection(self,category,is_dialog=False,dialog=None):
        if is_dialog:
            docs_category = ["bank","fee","result","student_id","death"]
            if category in docs_category:

                confirm = self.screen_manager.get_screen("confirm")
                confirm.prepare_document(category)
                confirm.generate_preview()
                confirm.preview()
            for k,v in self.selected_institution.items():
                v = False
                if k == category:
                    v=True
                self.selected_institution[k] = v
            apply = self.screen_manager.get_screen("apply")
            if self.dialog: self.dialog.dismiss(force=True)
            for k,v in self.selected_institution.items():
                if v: apply.ids.instcat.text = k
            
            apply.ids.instname.disabled = False
            apply.ids.admno.disabled = False
            apply.ids.curyear.disabled = False
            self.dialog = None
            
        for k,v in self.selected_gender.items():
            v = False
            if k == category:
                v=True
            self.selected_gender[k] = v
       
    def alert(self,text=None):
        if not text: text = "Something went wrong"
        snackbar = CustomSnackbar(
            text=text,
            icon="information",
            snackbar_x="10dp",
            snackbar_y="10dp",
            bg_color=rgba(125,202,222,255),
        )
        snackbar.size_hint_x = (
            Window.width - (snackbar.snackbar_x * 2)
        ) / Window.width
        snackbar.open()

    def hide(self):
        apply = self.screen_manager.get_screen("apply")
        home = self.screen_manager.get_screen("home")
        sid = apply.ids.sid_preview
        bank = apply.ids.bank_preview
        fee = apply.ids.fee_preview
        result = apply.ids.result_preview
        death = apply.ids.death_preview
        approvebtn = home.ids.approvebtn
        applybtn = home.ids.applybtn

        hide_all = [sid, bank, fee, death, approvebtn, applybtn, result]
        for x in hide_all:
            self.hide_widget(x,dohide=True)

    def build(self):
        self.screen_manager.add_widget(Builder.load_file("widgets/welcome.kv"))
        self.screen_manager.add_widget(Builder.load_file("widgets/signin.kv"))
        self.screen_manager.add_widget(Builder.load_file("widgets/register.kv"))
        self.screen_manager.add_widget(Builder.load_file("widgets/forgot.kv"))
        self.screen_manager.add_widget(Builder.load_file("widgets/home.kv"))
        self.screen_manager.add_widget(Builder.load_file("widgets/apply.kv"))
        self.screen_manager.add_widget(Builder.load_file("widgets/update.kv"))
        self.screen_manager.add_widget(Builder.load_file("widgets/approve.kv"))
        self.screen_manager.add_widget(Builder.load_file("widgets/preview.kv"))
        self.screen_manager.add_widget(Builder.load_file("widgets/confirm.kv"))
        
        self.hide()
        
        return self.screen_manager

if __name__ == "__main__":
    LabelBase.register(name="MPoppins",fn_regular="assets/fonts/Poppins/Poppins-Medium.ttf")
    LabelBase.register(name="BPoppins",fn_regular="assets/fonts/Poppins/Poppins-Bold.ttf")
    LabelBase.register(name="BIPoppins",fn_regular="assets/fonts/Poppins/Poppins-BoldItalic.ttf")
    LabelBase.register(name="Motion",fn_regular="assets/fonts/motion-font/motion.ttf")
    EMSApp().run()
