import sqlite3
from random import randint

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.lang import Builder
from kivy.uix.popup import Popup

import administration_database as adm
import student_database as std

adm.create_admin_database()
std.create_st_database()


class WindowManager(ScreenManager):
    pass


class HomeScreen(Screen):

    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)

        self.user = 'admin'

        # the admin sign up page will open if there is no admin (on the first opening of app)
        if len(adm.fetch_admin_data()) == 0:
            self.sign_up_window()

        # admin login page if no student otherwise student login page will be seen
        else:
            self.sign_in_window()

    def sign_up_window(self):  # <= sign up window opens only the first time for administrator to signing up!

        self.box = BoxLayout(orientation='vertical',
                             size_hint=(0.5, 0.8),
                             pos_hint={'x': (0.5 - 0.25), 'y': 0.15})
        self.grd = GridLayout()
        self.grd.cols = 1
        self.grd.rows = 3

        self.heading = Label(text='Admin Sign Up')
        self.grd.add_widget(self.heading)

        self.top_grd = GridLayout()
        self.top_grd.cols = 1
        self.top_grd.rows = 2
        self.adm_username = TextInput(hint_text='admin username...', multiline=False, )
        self.adm_password = TextInput(hint_text='admin password...', multiline=False)
        self.top_grd.add_widget(self.adm_username)
        self.top_grd.add_widget(self.adm_password)

        self.grd.add_widget(self.top_grd)

        self.confirm_sign_up = Button(text='Sign Up')
        self.confirm_sign_up.bind(on_release=self.sign_up_btn)
        self.grd.add_widget(self.confirm_sign_up)

        self.box.add_widget(self.grd)
        self.add_widget(self.box)

    def sign_in_window(self):  # <= opens everytime for admin and students to sign up!

        self.box = BoxLayout(orientation='vertical',
                             size_hint=(0.5, 0.8),
                             pos_hint={'x': (0.5 - 0.25), 'y': 0.15})
        self.grd = GridLayout()
        self.grd.cols = 1
        self.grd.rows = 3

        students = [v[0] for v in adm.fetch_student()]
        if len(students) != 0:
            self.user = 'student'
            self.heading = Label(text='Student Login')
            self.username = TextInput(hint_text='student username...', multiline=False)
            self.password = TextInput(hint_text='student password...', multiline=False)
            self.change_user_btn = Button(text='go to admin log in!')
            self.change_user_btn.bind(on_release=self.go_to_btn)
        else:
            self.heading = Label(text='Admin Login')
            self.username = TextInput(hint_text='admin username...', multiline=False)
            self.password = TextInput(hint_text='admin password...', multiline=False)
            self.change_user_btn = Button(text='go to student log in!', disabled=True)
            self.change_user_btn.bind(on_release=self.go_to_btn)

        self.grd.add_widget(self.heading)
        self.top_grd = GridLayout()
        self.top_grd.cols = 1
        self.top_grd.rows = 2
        self.top_grd.add_widget(self.username)
        self.top_grd.add_widget(self.password)

        self.grd.add_widget(self.top_grd)

        self.btm_grd = GridLayout()
        self.btm_grd.cols = 1
        self.btm_grd.rows = 2

        self.confirm_log_in = Button(text='Log In')
        self.confirm_log_in.bind(on_release=self.log_in_btn)
        self.btm_grd.add_widget(self.confirm_log_in)
        self.btm_grd.add_widget(self.change_user_btn)

        self.grd.add_widget(self.btm_grd)
        self.box.add_widget(self.grd)
        self.add_widget(self.box)

    def sign_up_btn(self, instance):  # Add admin data to the sqlite3 database
        admin_username = self.adm_username.text
        admin_password = self.adm_password.text
        db = sqlite3.connect('admin_database.db')
        c = db.cursor()
        c.execute("INSERT INTO admin_data VALUES(?,?,'FALSE','FALSE','FALSE','[]')", (admin_username, admin_password))
        db.commit()
        db.close()
        self.manager.get_screen("AdminDash").showPop("Sign Up Completed!")
        self.remove_widget(self.box)
        self.sign_in_window()

    def log_in_btn(self, instance):
        if self.heading.text == "Admin Login":
            admin_username = adm.fetch_admin_data()[0][0]
            admin_password = adm.fetch_admin_data()[0][1]
            if self.username.text == admin_username and self.password.text == admin_password:
                self.manager.current = 'AdminDash'
                self.manager.transition.direction = 'left'
                self.username.text = ''
                self.password.text = ''
            else:
                if self.username.text != admin_username and self.password.text != admin_password:
                    self.manager.get_screen("AdminDash").showPop("Wrong username and password!")
                elif self.username.text != admin_username:
                    self.manager.get_screen("AdminDash").showPop("Wrong username!")
                else:
                    self.manager.get_screen("AdminDash").showPop("Wrong password!")

        else:
            try:
                student_password = [v[1] for v in adm.fetch_student() if v[0] == self.username.text][0]
                if self.password.text == student_password:

                    self.manager.get_screen('StudentDash').do_stuffs()
                    self.manager.current = 'StudentDash'
                    self.manager.transition.direction = 'left'
                else:
                    self.manager.get_screen("AdminDash").showPop("Wrong Password!")

            except IndexError:
                self.manager.get_screen("AdminDash").showPop(f"No student named {self.username.text}")

    def go_to_btn(self, instance):  # <= to swtich between admin and student login
        if self.change_user_btn.text == "go to admin log in!":
            self.heading.text = 'Admin Login'
            self.change_user_btn.text = "go to student log in!"
            self.username.hint_text = 'admin username...'
            self.password.hint_text = 'admin password...'
            self.username.text = ''
            self.password.text = ''
        else:
            self.heading.text = 'Student Login'
            self.change_user_btn.text = "go to admin log in!"
            self.username.hint_text = 'student username...'
            self.user = "student"
            self.password.hint_text = 'student password...'
            self.username.text = ''
            self.password.text = ''


class ConfirmationWindow(Screen):  # all confirmation comes to here...
    def __init__(self, **kwargs):
        super(ConfirmationWindow, self).__init__(**kwargs)

        self.prev_window = ''
        self.confirm = ''

    def back_button(self):
        self.manager.current = self.prev_window

    def confirm_btn(self):
        if self.confirm == 'lock_dept':
            adm.lock_departments()
            self.manager.get_screen("AddRecordWindow").dept_lock_status = "TRUE"
            self.manager.get_screen("AddRecordWindow").remove_widget(self.manager.get_screen("AddRecordWindow").box)
            self.manager.get_screen("AddRecordWindow").add_student_window()
            self.manager.current = 'AdminDash'

        elif self.confirm == 'dept_choice':
            new_data = 'FALSE' if adm.fetch_admin_data()[0][2] == 'TRUE' else 'TRUE'
            adm.update_admin_data('admin_data', 'subject_choice_enabled', new_data)
            self.manager.get_screen("AdminDash").department_choice_status = "Enabled" if adm.fetch_admin_data()[0][
                                                                                             2] == "TRUE" else "Disabled"
            self.manager.get_screen(
                "AdminDash").change_choice_cmd = "Enable" if self.manager.get_screen(
                "AdminDash").department_choice_status == "Disabled" else "Disable"
            self.manager.current = 'AdminDash'

        elif self.confirm == "publish_result":
            self.manager.get_screen("AdminDash").publish_result()
            self.manager.get_screen("AddRecordWindow").result_publish_status = 'TRUE'
            self.manager.current = 'AdminDash'

        elif self.confirm == 'cancel_admission':
            adm.cancel_student(self.manager.get_screen("StudentDash").student_name)
            self.manager.get_screen("AdminDash").publish_result()
            self.manager.get_screen('HomeScreen').username.text = ''
            self.manager.get_screen('HomeScreen').password.text = ''
            self.manager.current = "HomeScreen"
            self.manager.transition.direction = 'right'
            self.manager.get_screen("AdminDash").showPop("You have successfully canceled your admission!")



# admin panel
class AdminDash(Screen):

    def __init__(self, **kwargs):
        super(AdminDash, self).__init__(**kwargs)

        try:
            self.department_choice_status = "Enabled" if adm.fetch_admin_data()[0][2] == "TRUE" else "Disabled"
            self.change_choice_cmd = "Enable" if self.department_choice_status == "Disabled" else "Disable"
        except IndexError:
            self.department_choice_status = "Disabled"
            self.change_choice_cmd = "Enable"

    def showPop(self, text):  # calls the Popup()
        return Popup(content=Label(text=text), size_hint=(dp(.4), dp(.15)),
                     pos_hint={'x': 0.095, 'top': .9}).open()

    def dept_lock_btn(self):  # <= check and lock departments and if not locked show pop up!
        departments = [v[0] for v in adm.fetch_departments()[0]]
        if adm.fetch_admin_data()[0][3] == "FALSE" and len(departments) >= 3:
            self.manager.get_screen("ConfirmationWindow").prev_window = "AdminDash"
            self.manager.get_screen("ConfirmationWindow").confirm = "lock_dept"
            self.manager.current = "ConfirmationWindow"
        else:
            if adm.fetch_admin_data()[0][3] == "TRUE":
                self.showPop("Departments already locked!")
            else:
                self.showPop("Please Add at least 3 departments!")

    def dept_locked_popup(self):
        if self.manager.get_screen("AddRecordWindow").dept_lock_status == "TRUE":
            return self.showPop("Departments are locked!")

    def dept_not_locked_popup(self):
        if self.manager.get_screen("AddRecordWindow").dept_lock_status == "FALSE":
            return self.showPop("Departments are not locked!")

    def result_published_popup(self):
        if self.manager.get_screen("AddRecordWindow").result_publish_status == "TRUE":
            return self.showPop("No students can be added now\nResult Has been Published!")

    def result_confirmation(self):

        if adm.fetch_admin_data()[0][4] == "FALSE" and len([v[0] for v in adm.fetch_student()]) >= 3:
            self.manager.get_screen("ConfirmationWindow").ids.confirm_label.text = "Are you sure you want to\n" \
                                                                                   "Publish the Result?"
            self.manager.get_screen("ConfirmationWindow").prev_window = "AdminDash"
            self.manager.get_screen("ConfirmationWindow").confirm = "publish_result"
            self.manager.current = "ConfirmationWindow"
        elif adm.fetch_admin_data()[0][4] == "TRUE":
            self.showPop("Result already Published!")
        else:
            self.showPop("Please Add at least 3 students!")

    def publish_result(self):
        for v in adm.get_merit():
            # selects the choices from student choices (not the primary one's from admin data)
            choice = std.fetch_dept_choice(v[0])
            for i in choice:
                # checks if the department has seats available else move on to next choice
                if adm.query_left_seat(i) > 0:
                    # as there is left seat update obtained department in the admin panel to student data
                    adm.update_obtained_dept(v[0], i)
                    # also update obtained department in the student panel
                    std.update_dept(i, v[0])
                    #update left seat : decrease number of seats by 1 in current department
                    adm.update_left_seat(i)
                    adm.update_admin_data('admin_data', 'result_published', 'TRUE')
                    break


class AddRecordWindow(Screen):

    def __init__(self, **kwargs):
        super(AddRecordWindow, self).__init__(**kwargs)
        try:
            self.dept_lock_status = adm.fetch_admin_data()[0][3]
            self.result_publish_status = adm.fetch_admin_data()[0][4]
        except IndexError:
            self.dept_lock_status = "FALSE"
            self.result_publish_status = "FALSE"

        self.box = BoxLayout(orientation='vertical',
                             size_hint=(0.5, 0.7),
                             padding=15,
                             pos_hint={'x': 0.25, 'y': 0.35},
                             spacing=100)

        self.name_label = Label(text='Student Name')
        self.name_input = TextInput(hint_text='type student name here...', multiline=False)
        self.marks_label = Label(text='Student Marks')
        self.marks_input = TextInput(hint_text='type student marks here...', multiline=False)

        self.dept_name_label = Label(text='Department Name : ')
        self.dept_name_input = TextInput(hint_text='type department name here...', multiline=False)
        self.seat_cap_label = Label(text='Department Seat Capacity')
        self.seat_cap_input = TextInput(hint_text='type seat capacity here...', multiline=False)

        if self.dept_lock_status == 'TRUE':
            self.add_student_window()
        else:
            self.add_department_window()

    def add_student_window(self):

        box = BoxLayout(orientation='vertical',
                        size_hint=(0.5, 0.7),
                        padding=15,
                        pos_hint={'x': 0.25, 'y': 0.35},
                        spacing=100)

        add_button = Button(text='Add Student')
        add_button.bind(on_release=self.add_record)

        top_grd = GridLayout(size_hint=(1, None), size=(100, 200))
        top_grd.cols = 2
        top_grd.rows = 2

        btm_grd = GridLayout(size_hint=(1, None))
        btm_grd.cols = 1
        btm_grd.rows = 1

        top_grd.add_widget(self.name_label)
        top_grd.add_widget(self.name_input)
        top_grd.add_widget(self.marks_label)
        top_grd.add_widget(self.marks_input)

        btm_grd.add_widget(add_button)

        box.add_widget(top_grd)
        box.add_widget(btm_grd)
        self.add_widget(box)

    def add_department_window(self):

        add_button = Button(text='Add Department')
        add_button.bind(on_release=self.add_record)

        top_grd = GridLayout(size_hint=(1, None), size=(100, 200))
        top_grd.cols = 2
        top_grd.rows = 2

        btm_grd = GridLayout(size_hint=(1, None))
        btm_grd.cols = 1
        btm_grd.rows = 1

        top_grd.add_widget(self.dept_name_label)
        top_grd.add_widget(self.dept_name_input)
        top_grd.add_widget(self.seat_cap_label)
        top_grd.add_widget(self.seat_cap_input)

        btm_grd.add_widget(add_button)

        self.box.add_widget(top_grd)
        self.box.add_widget(btm_grd)
        self.add_widget(self.box)

    def add_record(self, instance):
        if self.dept_lock_status == 'TRUE':

            """this is primary (first-time) department
                choice serial according to added department by admin"""
            students = [v[0] for v in adm.fetch_student()]

            name = self.name_input.text.lower().capitalize()
            temp_list = []
            std_pass = randint(1001, 1999)
            if std_pass in temp_list:
                while std_pass in temp_list:
                    std_pass = randint(1001, 1999)
            temp_list.append(std_pass)
            try:
                marks = int(self.marks_input.text)
                if 0 <= marks <= 100:
                    if name not in students:
                        primary_dept_choice = adm.fetch_admin_data()[0][5]
                        adm.input_std_data(name, std_pass, marks, primary_dept_choice, '')
                        std.add_std_data(name, primary_dept_choice, 'ON', '')
                        self.manager.get_screen("HomeScreen").change_user_btn.disabled = False
                        self.name_input.text = ''
                        self.marks_input.text = ''
                    else:
                        self.manager.get_screen("AdminDash").showPop("Student Already Registered!")
                else:
                    self.manager.get_screen("AdminDash").showPop("Please Type valid Marks!")
            except ValueError:
                self.manager.get_screen("AdminDash").showPop("Please Type valid Marks!")

        else:
            dept_name = self.dept_name_input.text
            departments = [v[0] for v in adm.fetch_departments()[0]]
            try:

                seat_capacity = int(self.seat_cap_input.text)
                if dept_name not in departments and seat_capacity > 0:
                    adm.input_departments(dept_name, seat_capacity, seat_capacity)
                    adm.input_primary_department_choice(dept_name)
                else:
                    if seat_capacity < 0:
                        self.manager.get_screen("AdminDash").showPop("Please Type valid seat capacity!")
                    else:
                        self.manager.get_screen("AdminDash").showPop("Department Already Registered!")
                self.dept_name_input.text = ''
                self.seat_cap_input.text = ''

            except ValueError:
                self.manager.get_screen("AdminDash").showPop("Please Type valid seat capacity!")


class ShowAllStudentsWindow(Screen):
    def __init__(self, **kwargs):
        super(ShowAllStudentsWindow, self).__init__(**kwargs)

        self.student_name = ''
        self.student_marks = 0
        self.obt_dept = ''
        self.btn_dic = {}

    def do_stuffs(self):

        if self.manager.get_screen("AddRecordWindow").result_publish_status == "FALSE":
            self.manager.get_screen("AdminDash").showPop("Result Not Published Yet!")

        self.box = BoxLayout(orientation='vertical',
                             size_hint=(0.5, 0.8),
                             pos_hint={'x': (0.5 - 0.25), 'y': 0.12})

        self.grd = GridLayout()
        self.grd.cols = 1
        self.grd.rows = len([v[0] for v in adm.fetch_student()])

        for v in range(len([v[0] for v in adm.fetch_student()])):
            if adm.fetch_student()[v][0] == [v[0] for v in adm.fetch_student()][v]:
                self.obt_dept = adm.fetch_student()[v][4]
                self.std_btn = ToggleButton(text=f"{[v[0] for v in adm.fetch_student()][v]} : {self.obt_dept}")
                self.std_btn.id = f'student{v}'
                self.btn_dic[self.std_btn.id] = self.std_btn
                self.std_btn.bind(on_release=self.std_record)
                self.grd.add_widget(self.std_btn)
        self.box.add_widget(self.grd)
        self.add_widget(self.box)

    def std_record(self, instance):

        for v in range(len([v[0] for v in adm.fetch_student()])):
            if self.btn_dic[f'student{v}'].state == "down":
                self.student_name = self.btn_dic[f'student{v}'].text.split(" ")[0]
                self.obt_dept = self.btn_dic[f'student{v}'].text.split(" ")[-1]
                if adm.fetch_student()[v][0] == self.student_name:
                    self.student_marks = adm.fetch_student()[v][2]
                self.manager.get_screen("StudentDataWindow").student_name.text = f"Name : {str(self.student_name)}"
                self.manager.get_screen(
                    "StudentDataWindow").student_marks.text = f"Marks : {str(self.student_marks)}"
                self.manager.get_screen(
                    "StudentDataWindow").obt_dept.text = f"Obtained Department : {str(self.obt_dept)}"
                self.manager.current = "StudentDataWindow"
                for i in self.btn_dic.values():
                    i.state = 'normal'


class StudentDataWindow(Screen):
    def __init__(self, **kwargs):
        super(StudentDataWindow, self).__init__(**kwargs)

        self.box = BoxLayout(orientation='vertical',
                             size_hint=(0.5, 0.8),
                             pos_hint={'x': (0.5 - 0.25), 'y': 0.12})

        self.top_grid = GridLayout()
        self.top_grid.rows = 1
        self.top_grid.cols = 1

        self.label = Label(text="Student Record")
        self.top_grid.add_widget(self.label)

        self.btm_grid = GridLayout()
        self.btm_grid.cols = 1
        self.btm_grid.rows = 3

        self.student_name = Label()
        self.student_marks = Label()
        self.obt_dept = Label()

        self.btm_grid.add_widget(self.student_name)
        self.btm_grid.add_widget(self.student_marks)
        self.btm_grid.add_widget(self.obt_dept)

        self.box.add_widget(self.top_grid)
        self.box.add_widget(self.btm_grid)
        self.add_widget(self.box)


# student_panel
class StudentDash(Screen):
    def __init__(self, **kwargs):
        super(StudentDash, self).__init__(**kwargs)

        self.student_name = ''

    def do_stuffs(self):
        # This section is under top grid layout
        self.student_name = self.manager.get_screen("HomeScreen").username.text
        self.box = BoxLayout(orientation="vertical",
                             spacing=50,
                             padding=20,
                             size_hint=(0.5, 0.7),
                             pos_hint={'x': 0.25, 'y': 0.15})

        top_grd = GridLayout()
        top_grd.cols = 1
        top_grd.rows = 3

        scrl = ScrollView()

        top_grd_sub = GridLayout()
        top_grd_sub.cols = 2
        top_grd_sub.rows = 1

        btm_grd = GridLayout()
        btm_grd.cols = 1
        btm_grd.rows = 2

        name_label = Label(text=f"Name : {self.student_name}")
        try:
            dept_label = Label(
                text=f"Department Name : {std.query_std('std_data', 'obtained_dept', 'name', self.student_name)[0][0]}")
        except IndexError:
            dept_label = Label(text='')

        self.migration_label = Label(text="Migration")
        self.migration_btn = Button(text="Turn Off")
        top_grd_sub.add_widget(self.migration_label)
        top_grd_sub.add_widget(self.migration_btn)

        # adding widgets top grid layout
        top_grd.add_widget(name_label)
        top_grd.add_widget(dept_label)
        top_grd.add_widget(top_grd_sub)

        # this section is under middle scroll view layout
        choice_list = Label(text=self.show_choice_list())

        # adding widgets to scroll view layout
        scrl.add_widget(choice_list)

        # this section is under bottom grid layout
        change_btn = Button(text='CHANGE CHOICE LIST')
        change_btn.bind(on_release=self.change_choice)
        cancel_btn = Button(text='CANCEL ADMISSION')
        cancel_btn.bind(on_release=self.cancel_adm)

        # adding widgets to bottom grid layout
        btm_grd.add_widget(change_btn)
        btm_grd.add_widget(cancel_btn)

        # adding all layouts to the parent box layout
        self.box.add_widget(top_grd)
        self.box.add_widget(scrl)
        self.box.add_widget(btm_grd)
        self.add_widget(self.box)

    def log_out(self):
        self.manager.get_screen('HomeScreen').username.text = ''
        self.manager.get_screen('HomeScreen').password.text = ''
        self.manager.get_screen('ConfirmationWindow').prev_window = 'HomeScreen'
        self.manager.get_screen('ConfirmationWindow').back_button()
        self.manager.transition.direction = 'right'
        self.box.clear_widgets()

    def show_choice_list(self):
        choices = ''
        # try: except IndexError: pass
        for v in range(len(std.fetch_dept_choice(self.student_name))):
            choices += f'\n{v + 1} : {std.fetch_dept_choice(self.student_name)[v]}'
        return choices

    def change_choice(self, instance):
        if adm.fetch_admin_data()[0][2] == "TRUE" and adm.fetch_admin_data()[0][4] == "FALSE":
            self.manager.get_screen("ChangeDeptChoiceWindow").do_stuffs()
            self.manager.current = 'ChangeDeptChoiceWindow'
        else:
            if adm.fetch_admin_data()[0][2] == "FALSE":
                self.manager.get_screen("AdminDash").showPop("Department Choice is DISABLED by Admin")
            else:
                self.manager.get_screen("AdminDash").showPop(
                    "Result Has Been Published!\nYou cannot change department choice anymore!")

    def cancel_adm(self, instance):
        if self.manager.get_screen("AddRecordWindow").result_publish_status == "TRUE":
            self.manager.get_screen("ConfirmationWindow").prev_window = 'StudentDash'
            self.manager.get_screen("ConfirmationWindow").confirm = 'cancel_admission'
            self.manager.current = "ConfirmationWindow"
        else:
            self.manager.get_screen("AdminDash").showPop("Sorry! Result has not been published yet.")


class ChangeDeptChoiceWindow(Screen):
    def __init__(self, **kwargs):
        super(ChangeDeptChoiceWindow, self).__init__(**kwargs)

        self.btn_dic = {}
        self.btns_clicked = []
        self.btn_number_labels = []
        self.departments = [v[0] for v in adm.fetch_departments()[0]]
        self.student_name = ''

    def do_stuffs(self):
        self.student_name = self.manager.get_screen("HomeScreen").username.text
        box = BoxLayout(orientation='vertical',
                        size_hint=(0.5, 0.8),
                        pos_hint={'x': (0.5 - 0.25), 'y': 0.12})

        top_grd = GridLayout()
        top_grd.cols = 1
        top_grd.rows = len(eval([v[3] for v in adm.fetch_student()][0]))
        for v in range(1, (len(std.fetch_dept_choice(self.student_name)) + 1)):
            dept_btn = ToggleButton(text=std.fetch_dept_choice(self.student_name)[v - 1])
            dept_btn.id = f'btn{v}'
            self.btn_dic[dept_btn.id] = dept_btn
            dept_btn.bind(on_press=self.record_depts)
            top_grd.add_widget(dept_btn)

        btm_grd = GridLayout()
        btm_grd.cols = 1
        btm_grd.rows = 1
        back_btn = Button(text="CONFIRM AND GO BACK")
        back_btn.bind(on_release=self.back_button)
        btm_grd.add_widget(back_btn)

        box.add_widget(top_grd)
        box.add_widget(btm_grd)
        self.add_widget(box)

    def record_depts(self, instance):
        for v in self.btn_dic.values():
            if v.state == 'down' and v not in self.btns_clicked:
                self.btns_clicked.append(v)
                v.text = f'{self.btns_clicked.index(v) + 1} {v.text}'
            if v.state == 'normal' and v in self.btns_clicked:
                self.btns_clicked.remove(v)
                v.text = v.text.split(" ")[1]
                for i in self.btn_dic.values():
                    if i.state == 'down' and i in self.btns_clicked:
                        i.text = f'{self.btns_clicked.index(i) + 1} {i.text.split(" ")[1]}'

    def back_button(self, instance):
        all_selected = True
        none_selected = True
        for v in self.btn_dic.values():
            if v.state == 'normal':
                all_selected = False
                break

        for v in self.btn_dic.values():
            if v.state == 'down':
                none_selected = False
                break

        if all_selected:
            new_choices = []
            for v in self.btns_clicked:
                new_choices.append(v.text.split(" ")[1])
            adm.update_std_data('std_data', 'dept_choice', repr(new_choices), self.student_name)
            std.update_std_data('std_data', 'dept_choice', repr(new_choices), self.student_name)
            self.manager.get_screen("StudentDash").box.clear_widgets()
            self.manager.get_screen("StudentDash").do_stuffs()
            self.manager.current = "StudentDash"
            self.manager.transition.direction = 'right'
            self.btns_clicked.clear()

        elif none_selected:
            self.manager.get_screen("StudentDash").box.clear_widgets()
            self.manager.get_screen("StudentDash").do_stuffs()
            self.manager.current = "StudentDash"
            self.manager.transition.direction = 'right'
            self.btns_clicked.clear()

        else:
            self.manager.get_screen("AdminDash").showPop("All Departments not Selected")


kvFile = Builder.load_file("subjectManagement.kv")


class SubjectManagementApp(App):
    def build(self):
        # return ShowAllStudentsWindow()
        return kvFile


SubjectManagementApp().run()
