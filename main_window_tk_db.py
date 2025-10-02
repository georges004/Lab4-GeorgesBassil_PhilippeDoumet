import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from Student import Student
from Instructor import Instructor
from Course import Course
import db


def refresh_instructor_combo():
    instructor_combo["values"] = [f"{i['instructor_id']} - {i['name']}" for i in db.list_instructors()]

def refresh_student_combo():
    register_student_combo["values"] = [f"{s['student_id']} - {s['name']}" for s in db.list_students()]

def refresh_course_combos():
    vals = [f"{c['course_id']} - {c['course_name']}" for c in db.list_courses()]
    register_course_combo["values"] = vals
    assign_course_combo["values"] = vals

def refresh_instructor_assign_combo():
    assign_instructor_combo["values"] = [f"{i['instructor_id']} - {i['name']}" for i in db.list_instructors()]

def refresh_all_tables():
    for i in students_tree.get_children(): students_tree.delete(i)
    for s in db.list_students():
        course_list = ", ".join(db.student_courses(s["student_id"]))
        students_tree.insert("", tk.END, values=(s["student_id"], s["name"], s["age"], s["email"], course_list))

    for i in instructors_tree.get_children(): instructors_tree.delete(i)
    for ins in db.list_instructors():
        course_list = ", ".join(db.instructor_courses(ins["instructor_id"]))
        instructors_tree.insert("", tk.END, values=(ins["instructor_id"], ins["name"], ins["age"], ins["email"], course_list))

    for i in courses_tree.get_children(): courses_tree.delete(i)
    for c in db.list_courses():
        instr = c["instructor_id"] or ""
        roster = ", ".join(db.course_students(c["course_id"]))
        courses_tree.insert("", tk.END, values=(c["course_id"], c["course_name"], instr, roster))

def clear_student_form():
    stu_name.delete(0, tk.END); stu_age.delete(0, tk.END); stu_email.delete(0, tk.END); stu_id.delete(0, tk.END)

def clear_instructor_form():
    ins_name.delete(0, tk.END); ins_age.delete(0, tk.END); ins_email.delete(0, tk.END); ins_id.delete(0, tk.END)

def clear_course_form():
    course_id.delete(0, tk.END); course_name.delete(0, tk.END); instructor_combo.set("")

def add_student():
    try:
        s = Student(stu_name.get().strip(), int(stu_age.get()), stu_email.get().strip(), stu_id.get().strip())
        db.add_student(s.student_id, s.name, s.age, s._email)
        clear_student_form()
        refresh_student_combo(); refresh_all_tables()
        messagebox.showinfo("OK", "Student added")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def update_student():
    try:
        sid = stu_id.get().strip()
        name = stu_name.get().strip()
        age = int(stu_age.get())
        email = stu_email.get().strip()
        Student(name, age, email, sid)
        db.update_student(sid, name, age, email)
        refresh_student_combo(); refresh_all_tables()
        messagebox.showinfo("OK", "Student updated")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def delete_student():
    try:
        sid = stu_id.get().strip()
        if not sid:
            sel = students_tree.selection()
            if sel: sid = students_tree.item(sel[0], "values")[0]
        if not sid: raise ValueError("select a student (row or ID)")
        db.delete_student(sid)
        clear_student_form()
        refresh_student_combo(); refresh_all_tables()
        messagebox.showinfo("OK", "Student deleted")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def add_instructor():
    try:
        i = Instructor(ins_name.get().strip(), int(ins_age.get()), ins_email.get().strip(), ins_id.get().strip())
        db.add_instructor(i.instructor_id, i.name, i.age, i._email)
        clear_instructor_form()
        refresh_instructor_combo(); refresh_instructor_assign_combo(); refresh_all_tables()
        messagebox.showinfo("OK", "Instructor added")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def update_instructor():
    try:
        iid = ins_id.get().strip()
        name = ins_name.get().strip()
        age = int(ins_age.get())
        email = ins_email.get().strip()
        Instructor(name, age, email, iid)
        db.update_instructor(iid, name, age, email)
        refresh_instructor_combo(); refresh_instructor_assign_combo(); refresh_all_tables()
        messagebox.showinfo("OK", "Instructor updated")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def delete_instructor():
    try:
        iid = ins_id.get().strip()
        if not iid:
            sel = instructors_tree.selection()
            if sel: iid = instructors_tree.item(sel[0], "values")[0]
        if not iid: raise ValueError("select an instructor (row or ID)")
        db.delete_instructor(iid)
        clear_instructor_form()
        refresh_instructor_combo(); refresh_instructor_assign_combo(); refresh_all_tables()
        messagebox.showinfo("OK", "Instructor deleted")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def add_course():
    try:
        cid = course_id.get().strip()
        cname = course_name.get().strip()
        sel = instructor_combo.get().strip()
        instr_id = sel.split(" - ", 1)[0] if sel else None
        Course(cid, cname, None)
        db.add_course(cid, cname, instr_id)
        clear_course_form()
        refresh_course_combos(); refresh_all_tables()
        messagebox.showinfo("OK", "Course added")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def update_course():
    try:
        cid = course_id.get().strip()
        cname = course_name.get().strip()
        sel = instructor_combo.get().strip()
        instr_id = sel.split(" - ", 1)[0] if sel else None
        Course(cid, cname, None)
        db.update_course(cid, cname, instr_id)
        refresh_instructor_combo(); refresh_instructor_assign_combo(); refresh_course_combos(); refresh_all_tables()
        messagebox.showinfo("OK", "Course updated")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def delete_course():
    try:
        cid = course_id.get().strip()
        if not cid:
            sel = courses_tree.selection()
            if sel: cid = courses_tree.item(sel[0], "values")[0]
        if not cid: raise ValueError("select a course (row or ID)")
        db.delete_course(cid)
        clear_course_form()
        refresh_course_combos(); refresh_all_tables()
        messagebox.showinfo("OK", "Course deleted")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def register_student_to_course():
    try:
        s_sel = register_student_combo.get().strip()
        c_sel = register_course_combo.get().strip()
        if not s_sel or not c_sel: raise ValueError("select a student and a course")
        sid = s_sel.split(" - ", 1)[0]
        cid = c_sel.split(" - ", 1)[0]
        db.enroll_student(sid, cid)
        refresh_all_tables()
        messagebox.showinfo("OK", "Student registered to course")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def assign_instructor_to_course():
    try:
        i_sel = assign_instructor_combo.get().strip()
        c_sel = assign_course_combo.get().strip()
        if not i_sel or not c_sel: raise ValueError("select an instructor and a course")
        iid = i_sel.split(" - ", 1)[0]
        cid = c_sel.split(" - ", 1)[0]
        db.assign_instructor(cid, iid)
        refresh_all_tables()
        messagebox.showinfo("OK", "Instructor assigned to course")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def on_students_select(_):
    sel = students_tree.selection()
    if not sel: return
    sid, name, age, email, _courses = students_tree.item(sel[0], "values")
    stu_id.delete(0, tk.END); stu_id.insert(0, sid)
    stu_name.delete(0, tk.END); stu_name.insert(0, name)
    stu_age.delete(0, tk.END); stu_age.insert(0, age)
    stu_email.delete(0, tk.END); stu_email.insert(0, email)

def on_instructors_select(_):
    sel = instructors_tree.selection()
    if not sel: return
    iid, name, age, email, _courses = instructors_tree.item(sel[0], "values")
    ins_id.delete(0, tk.END); ins_id.insert(0, iid)
    ins_name.delete(0, tk.END); ins_name.insert(0, name)
    ins_age.delete(0, tk.END); ins_age.insert(0, age)
    ins_email.delete(0, tk.END); ins_email.insert(0, email)

def on_courses_select(_):
    sel = courses_tree.selection()
    if not sel: return
    cid, name, instr, _students = courses_tree.item(sel[0], "values")
    course_id.delete(0, tk.END); course_id.insert(0, cid)
    course_name.delete(0, tk.END); course_name.insert(0, name)
    if instr:
        for i in db.list_instructors():
            if i["instructor_id"] == instr:
                instructor_combo.set(f"{i['instructor_id']} - {i['name']}"); break
    else:
        instructor_combo.set("")

def update_selected():
    tab = notebook.index(notebook.select())
    if tab == 0:
        sel = students_tree.selection()
        if not sel: return messagebox.showerror("Error", "select a student row")
        sid = students_tree.item(sel[0], "values")[0]
        stu_id.delete(0, tk.END); stu_id.insert(0, sid)
        update_student()
    elif tab == 1:
        sel = instructors_tree.selection()
        if not sel: return messagebox.showerror("Error", "select an instructor row")
        iid = instructors_tree.item(sel[0], "values")[0]
        ins_id.delete(0, tk.END); ins_id.insert(0, iid)
        update_instructor()
    else:
        sel = courses_tree.selection()
        if not sel: return messagebox.showerror("Error", "select a course row")
        cid = courses_tree.item(sel[0], "values")[0]
        course_id.delete(0, tk.END); course_id.insert(0, cid)
        update_course()

def delete_selected():
    tab = notebook.index(notebook.select())
    if tab == 0:
        sel = students_tree.selection()
        if not sel: return messagebox.showerror("Error", "select a student row")
        sid = students_tree.item(sel[0], "values")[0]
        stu_id.delete(0, tk.END); stu_id.insert(0, sid)
        delete_student()
    elif tab == 1:
        sel = instructors_tree.selection()
        if not sel: return messagebox.showerror("Error", "select an instructor row")
        iid = instructors_tree.item(sel[0], "values")[0]
        ins_id.delete(0, tk.END); ins_id.insert(0, iid)
        delete_instructor()
    else:
        sel = courses_tree.selection()
        if not sel: return messagebox.showerror("Error", "select a course row")
        cid = courses_tree.item(sel[0], "values")[0]
        course_id.delete(0, tk.END); course_id.insert(0, cid)
        delete_course()

def reload_from_db():
    refresh_instructor_combo(); refresh_instructor_assign_combo()
    refresh_student_combo(); refresh_course_combos(); refresh_all_tables()

def backup_db_ui():
    path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("SQLite DB","*.db")], initialfile="school_backup.db")
    if not path: return
    try:
        db.backup_db(path)
        messagebox.showinfo("Backup", f"Database backed up to:\n{path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def run_search(*_):
    term = search_var.get().strip().lower()
    tab = notebook.index(notebook.select())
    if tab == 0:
        for i in students_tree.get_children(): students_tree.delete(i)
        for s in db.list_students():
            courses = " ".join(db.student_courses(s["student_id"]))
            hay = f"{s['student_id']} {s['name']} {s['age']} {s['email']} {courses}".lower()
            if term in hay:
                students_tree.insert("", tk.END, values=(s["student_id"], s["name"], s["age"], s["email"], ", ".join(db.student_courses(s["student_id"]))))
    elif tab == 1:
        for i in instructors_tree.get_children(): instructors_tree.delete(i)
        for ins in db.list_instructors():
            courses = " ".join(db.instructor_courses(ins["instructor_id"]))
            hay = f"{ins['instructor_id']} {ins['name']} {ins['age']} {ins['email']} {courses}".lower()
            if term in hay:
                instructors_tree.insert("", tk.END, values=(ins["instructor_id"], ins["name"], ins["age"], ins["email"], ", ".join(db.instructor_courses(ins["instructor_id"]))))
    else:
        for i in courses_tree.get_children(): courses_tree.delete(i)
        for c in db.list_courses():
            instr = c["instructor_id"] or ""
            roster = " ".join(db.course_students(c["course_id"]))
            hay = f"{c['course_id']} {c['course_name']} {instr} {roster}".lower()
            if term in hay:
                courses_tree.insert("", tk.END, values=(c["course_id"], c["course_name"], instr, ", ".join(db.course_students(c["course_id"]))))


db.init_db()

root = tk.Tk()
root.title("School Management System (SQLite)")
root.geometry("1080x840")

top = ttk.Frame(root); top.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(8,0))
ttk.Label(top, text="Search:").pack(side="left")
search_var = tk.StringVar()
search_entry = ttk.Entry(top, textvariable=search_var, width=40); search_entry.pack(side="left", padx=6)
ttk.Button(top, text="Clear", command=lambda:(search_var.set(""), refresh_all_tables())).pack(side="left", padx=(4,10))
ttk.Button(top, text="Reload", command=reload_from_db).pack(side="left")
ttk.Button(top, text="Backup DB…", command=backup_db_ui).pack(side="left", padx=(6,0))
search_entry.bind("<KeyRelease>", run_search)

sf = ttk.LabelFrame(root, text="Add Student")
sf.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
ttk.Label(sf, text="Name").grid(row=0, column=0, sticky="w"); stu_name = ttk.Entry(sf); stu_name.grid(row=0, column=1, sticky="ew")
ttk.Label(sf, text="Age").grid(row=1, column=0, sticky="w"); stu_age = ttk.Entry(sf); stu_age.grid(row=1, column=1, sticky="ew")
ttk.Label(sf, text="Email").grid(row=2, column=0, sticky="w"); stu_email = ttk.Entry(sf); stu_email.grid(row=2, column=1, sticky="ew")
ttk.Label(sf, text="Student ID").grid(row=3, column=0, sticky="w"); stu_id = ttk.Entry(sf); stu_id.grid(row=3, column=1, sticky="ew")
ttk.Button(sf, text="Add", command=add_student).grid(row=4, column=0, columnspan=2, pady=6, sticky="ew")
sf.columnconfigure(1, weight=1)

if_ = ttk.LabelFrame(root, text="Add Instructor")
if_.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
ttk.Label(if_, text="Name").grid(row=0, column=0, sticky="w"); ins_name = ttk.Entry(if_); ins_name.grid(row=0, column=1, sticky="ew")
ttk.Label(if_, text="Age").grid(row=1, column=0, sticky="w"); ins_age = ttk.Entry(if_); ins_age.grid(row=1, column=1, sticky="ew")
ttk.Label(if_, text="Email").grid(row=2, column=0, sticky="w"); ins_email = ttk.Entry(if_); ins_email.grid(row=2, column=1, sticky="ew")
ttk.Label(if_, text="Instructor ID").grid(row=3, column=0, sticky="w"); ins_id = ttk.Entry(if_); ins_id.grid(row=3, column=1, sticky="ew")
ttk.Button(if_, text="Add", command=add_instructor).grid(row=4, column=0, columnspan=2, pady=6, sticky="ew")
if_.columnconfigure(1, weight=1)

cf = ttk.LabelFrame(root, text="Add Course")
cf.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
ttk.Label(cf, text="Course ID").grid(row=0, column=0, sticky="w"); course_id = ttk.Entry(cf); course_id.grid(row=0, column=1, sticky="ew")
ttk.Label(cf, text="Course Name").grid(row=1, column=0, sticky="w"); course_name = ttk.Entry(cf); course_name.grid(row=1, column=1, sticky="ew")
ttk.Label(cf, text="Instructor (optional)").grid(row=2, column=0, sticky="w")
instructor_combo = ttk.Combobox(cf, state="readonly"); instructor_combo.grid(row=2, column=1, sticky="ew")
ttk.Button(cf, text="Add", command=add_course).grid(row=3, column=0, columnspan=2, pady=6, sticky="ew")
cf.columnconfigure(1, weight=1)

regf = ttk.LabelFrame(root, text="Register Student to Course")
regf.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
ttk.Label(regf, text="Student").grid(row=0, column=0, sticky="w")
register_student_combo = ttk.Combobox(regf, state="readonly"); register_student_combo.grid(row=0, column=1, sticky="ew")
ttk.Label(regf, text="Course").grid(row=1, column=0, sticky="w")
register_course_combo = ttk.Combobox(regf, state="readonly"); register_course_combo.grid(row=1, column=1, sticky="ew")
ttk.Button(regf, text="Register", command=register_student_to_course).grid(row=2, column=0, columnspan=2, pady=6, sticky="ew")
regf.columnconfigure(1, weight=1)

asnf = ttk.LabelFrame(root, text="Assign Instructor to Course")
asnf.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")
ttk.Label(asnf, text="Instructor").grid(row=0, column=0, sticky="w")
assign_instructor_combo = ttk.Combobox(asnf, state="readonly"); assign_instructor_combo.grid(row=0, column=1, sticky="ew")
ttk.Label(asnf, text="Course").grid(row=1, column=0, sticky="w")
assign_course_combo = ttk.Combobox(asnf, state="readonly"); assign_course_combo.grid(row=1, column=1, sticky="ew")
ttk.Button(asnf, text="Assign", command=assign_instructor_to_course).grid(row=2, column=0, columnspan=2, pady=6, sticky="ew")
asnf.columnconfigure(1, weight=1)

nbf = ttk.LabelFrame(root, text="Records")
nbf.grid(row=4, column=0, columnspan=2, padx=10, pady=(0,6), sticky="nsew")
notebook = ttk.Notebook(nbf); notebook.pack(fill="both", expand=True)

students_frame = ttk.Frame(notebook); notebook.add(students_frame, text="Students")
students_tree = ttk.Treeview(students_frame, columns=("id","name","age","email","courses"), show="headings", height=8)
for col, txt, w in [("id","ID",120), ("name","Name",180), ("age","Age",60), ("email","Email",240), ("courses","Courses",260)]:
    students_tree.heading(col, text=txt); students_tree.column(col, width=w, anchor="w")
students_tree.pack(fill="both", expand=True)
students_tree.bind("<<TreeviewSelect>>", on_students_select)

instructors_frame = ttk.Frame(notebook); notebook.add(instructors_frame, text="Instructors")
instructors_tree = ttk.Treeview(instructors_frame, columns=("id","name","age","email","courses"), show="headings", height=8)
for col, txt, w in [("id","ID",120), ("name","Name",180), ("age","Age",60), ("email","Email",240), ("courses","Courses",260)]:
    instructors_tree.heading(col, text=txt); instructors_tree.column(col, width=w, anchor="w")
instructors_tree.pack(fill="both", expand=True)
instructors_tree.bind("<<TreeviewSelect>>", on_instructors_select)

courses_frame = ttk.Frame(notebook); notebook.add(courses_frame, text="Courses")
courses_tree = ttk.Treeview(courses_frame, columns=("id","name","instructor","students"), show="headings", height=8)
for col, txt, w in [("id","Course ID",120), ("name","Course Name",240), ("instructor","Instructor",140), ("students","Students",320)]:
    courses_tree.heading(col, text=txt); courses_tree.column(col, width=w, anchor="w")
courses_tree.pack(fill="both", expand=True)
courses_tree.bind("<<TreeviewSelect>>", on_courses_select)

actions = ttk.Frame(root)
actions.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=(0,10))
ttk.Button(actions, text="Update Selected", command=update_selected).pack(side="left", padx=(0,6))
ttk.Button(actions, text="Delete Selected", command=delete_selected).pack(side="left")

for r in range(1,6): root.rowconfigure(r, weight=0)
root.rowconfigure(4, weight=1)
root.columnconfigure(0, weight=1); root.columnconfigure(1, weight=1)

refresh_instructor_combo()
refresh_instructor_assign_combo()
refresh_student_combo()
refresh_course_combos()
refresh_all_tables()

search_entry.bind("<KeyRelease>", run_search)

root.mainloop()
