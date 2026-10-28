"""
admin_dashboard.py - Administrator GUI Interface

Provides a complete, professional desktop dashboard for the administrator to manage:
1. Student records (Add, View, Edit, Delete, Search, Create Login Accounts, Reset Passwords)
2. College announcements (Create, Publish, Edit, Delete)
3. Student leave requests (View, Filter, Approve, Reject with Comments, Delete)
4. Admin account settings (Secure Password Change)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

import student_management as sm
import announcement_management as am
import leave_management as lm
import auth


class AdminDashboardWindow:
    def __init__(self, root, admin_session, on_logout_callback):
        self.root = root
        self.admin_session = admin_session
        self.on_logout_callback = on_logout_callback
        
        top = self.root.winfo_toplevel()
        top.title(f"Student Management System - Admin Dashboard (Logged in as: {self.admin_session['username']})")
        top.geometry("1180x750")
        top.minsize(1050, 680)

        self._apply_styles()
        self._build_ui()
        self.load_all_data()

    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Color Palette
        bg_dark = "#1e293b"      # Slate navy header
        primary = "#2563eb"      # Vibrant blue
        secondary = "#0f766e"    # Teal
        accent = "#f59e0b"       # Amber
        danger = "#dc2626"       # Crimson red
        success = "#16a34a"      # Emerald green
        table_bg = "#ffffff"

        style.configure("Header.TFrame", background=bg_dark)
        style.configure("Header.TLabel", background=bg_dark, foreground="#ffffff", font=("Segoe UI", 16, "bold"))
        style.configure("HeaderSub.TLabel", background=bg_dark, foreground="#94a3b8", font=("Segoe UI", 10))

        # Notebook tabs
        style.configure("TNotebook", background="#f1f5f9", tabmargins=[10, 10, 10, 0])
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[16, 8])
        style.map("TNotebook.Tab",
                  background=[("selected", "#ffffff"), ("!selected", "#e2e8f0")],
                  foreground=[("selected", primary), ("!selected", "#475569")])

        # Treeview styling
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=26, background=table_bg)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e2e8f0", foreground="#1e293b")
        style.map("Treeview", background=[("selected", "#bfdbfe")], foreground=[("selected", "#0f172a")])

        # Button styling
        style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"), background=primary, foreground="#ffffff")
        style.map("Primary.TButton", background=[("active", "#1d4ed8")])

        style.configure("Success.TButton", font=("Segoe UI", 9, "bold"), background=success, foreground="#ffffff")
        style.map("Success.TButton", background=[("active", "#15803d")])

        style.configure("Danger.TButton", font=("Segoe UI", 9, "bold"), background=danger, foreground="#ffffff")
        style.map("Danger.TButton", background=[("active", "#b91c1c")])

        style.configure("Secondary.TButton", font=("Segoe UI", 9), background="#64748b", foreground="#ffffff")
        style.map("Secondary.TButton", background=[("active", "#475569")])

    def _build_ui(self):
        # 1. Top Header Frame
        header = ttk.Frame(self.root, style="Header.TFrame", height=65)
        header.pack(fill=tk.X, side=tk.TOP)

        title_box = ttk.Frame(header, style="Header.TFrame")
        title_box.pack(side=tk.LEFT, padx=20, pady=10)

        lbl_title = ttk.Label(title_box, text="STUDENT MANAGEMENT SYSTEM", style="Header.TLabel")
        lbl_title.pack(anchor="w")
        lbl_subtitle = ttk.Label(
            title_box, 
            text=f"Admin Portal | Logged in as: {self.admin_session['username']} | Administrator Access", 
            style="HeaderSub.TLabel"
        )
        lbl_subtitle.pack(anchor="w")

        btn_logout = ttk.Button(header, text="Logout", style="Danger.TButton", command=self.handle_logout)
        btn_logout.pack(side=tk.RIGHT, padx=20, pady=15)

        # 2. Main Tabbed Container
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Tab Frames
        self.tab_students = ttk.Frame(self.notebook)
        self.tab_announcements = ttk.Frame(self.notebook)
        self.tab_leaves = ttk.Frame(self.notebook)
        self.tab_settings = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_students, text="  Students Management  ")
        self.notebook.add(self.tab_announcements, text="  Announcements  ")
        self.notebook.add(self.tab_leaves, text="  Leave Requests  ")
        self.notebook.add(self.tab_settings, text="  Admin Settings  ")

        # Build each tab
        self._build_students_tab()
        self._build_announcements_tab()
        self._build_leaves_tab()
        self._build_settings_tab()

    # =========================================================================
    # TAB 1: STUDENT MANAGEMENT
    # =========================================================================
    def _build_students_tab(self):
        paned = ttk.PanedWindow(self.tab_students, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Left Panel: Student Input Form
        form_frame = ttk.LabelFrame(paned, text=" Student Details Form ", padding=12)
        paned.add(form_frame, weight=1)

        fields = [
            ("Student ID *:", "stu_id"),
            ("Full Name *:", "stu_name"),
            ("Age *:", "stu_age"),
            ("Gender *:", "stu_gender"),
            ("Course *:", "stu_course"),
            ("Department *:", "stu_dept"),
            ("Year of Study *:", "stu_year"),
            ("Email *:", "stu_email"),
            ("Phone *:", "stu_phone"),
            ("Address:", "stu_address")
        ]

        self.stu_vars = {}
        row = 0
        for label_text, var_name in fields:
            lbl = ttk.Label(form_frame, text=label_text, font=("Segoe UI", 9, "bold"))
            lbl.grid(row=row, column=0, sticky="w", pady=4, padx=4)

            if var_name == "stu_gender":
                var = tk.StringVar(value="Male")
                widget = ttk.Combobox(form_frame, textvariable=var, values=["Male", "Female", "Other"], state="readonly", width=25)
            elif var_name == "stu_year":
                var = tk.StringVar(value="1st Year")
                widget = ttk.Combobox(form_frame, textvariable=var, values=["1st Year", "2nd Year", "3rd Year", "4th Year", "Final Year"], state="readonly", width=25)
            elif var_name == "stu_address":
                var = tk.StringVar()
                widget = ttk.Entry(form_frame, textvariable=var, width=27)
            else:
                var = tk.StringVar()
                widget = ttk.Entry(form_frame, textvariable=var, width=27)

            widget.grid(row=row, column=1, sticky="w", pady=4, padx=4)
            self.stu_vars[var_name] = var
            row += 1

        # Form Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=12, sticky="ew")

        btn_add = ttk.Button(btn_frame, text="Add Student", style="Success.TButton", command=self.action_add_student)
        btn_add.grid(row=0, column=0, padx=2, pady=3, sticky="ew")

        btn_update = ttk.Button(btn_frame, text="Update", style="Primary.TButton", command=self.action_update_student)
        btn_update.grid(row=0, column=1, padx=2, pady=3, sticky="ew")

        btn_clear = ttk.Button(btn_frame, text="Clear", style="Secondary.TButton", command=self.clear_student_form)
        btn_clear.grid(row=0, column=2, padx=2, pady=3, sticky="ew")

        btn_delete = ttk.Button(btn_frame, text="Delete Record", style="Danger.TButton", command=self.action_delete_student)
        btn_delete.grid(row=1, column=0, columnspan=3, padx=2, pady=3, sticky="ew")

        # Account Credentials Section inside Left Panel
        acc_frame = ttk.LabelFrame(form_frame, text=" Student Login Credentials ", padding=8)
        acc_frame.grid(row=row+1, column=0, columnspan=2, sticky="ew", pady=8)

        ttk.Label(acc_frame, text="Username:").grid(row=0, column=0, sticky="w", pady=2)
        self.var_stu_user = tk.StringVar()
        ttk.Entry(acc_frame, textvariable=self.var_stu_user, width=22).grid(row=0, column=1, pady=2)

        ttk.Label(acc_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=2)
        self.var_stu_pwd = tk.StringVar()
        ttk.Entry(acc_frame, textvariable=self.var_stu_pwd, width=22, show="*").grid(row=1, column=1, pady=2)

        btn_acc_box = ttk.Frame(acc_frame)
        btn_acc_box.grid(row=2, column=0, columnspan=2, pady=6)
        ttk.Button(btn_acc_box, text="Create Login", style="Primary.TButton", command=self.action_create_account).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_acc_box, text="Reset Password", style="Secondary.TButton", command=self.action_reset_password).pack(side=tk.LEFT, padx=3)

        # Right Panel: Search Bar and Table
        table_container = ttk.Frame(paned)
        paned.add(table_container, weight=3)

        # Search Bar
        search_box = ttk.Frame(table_container, padding=6)
        search_box.pack(fill=tk.X, side=tk.TOP)

        ttk.Label(search_box, text="Search (ID / Name / Dept):", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=4)
        self.var_stu_search = tk.StringVar()
        entry_search = ttk.Entry(search_box, textvariable=self.var_stu_search, width=28)
        entry_search.pack(side=tk.LEFT, padx=4)
        entry_search.bind("<Return>", lambda e: self.action_search_students())

        ttk.Button(search_box, text="Search", style="Primary.TButton", command=self.action_search_students).pack(side=tk.LEFT, padx=3)
        ttk.Button(search_box, text="Reset Table", style="Secondary.TButton", command=self.load_students_table).pack(side=tk.LEFT, padx=3)

        # Treeview Table
        tree_frame = ttk.Frame(table_container)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "name", "age", "gender", "course", "dept", "year", "email", "phone", "account")
        self.tree_students = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

        self.tree_students.heading("id", text="Student ID")
        self.tree_students.heading("name", text="Name")
        self.tree_students.heading("age", text="Age")
        self.tree_students.heading("gender", text="Gender")
        self.tree_students.heading("course", text="Course")
        self.tree_students.heading("dept", text="Department")
        self.tree_students.heading("year", text="Year")
        self.tree_students.heading("email", text="Email")
        self.tree_students.heading("phone", text="Phone")
        self.tree_students.heading("account", text="Login User")

        self.tree_students.column("id", width=80, anchor="center")
        self.tree_students.column("name", width=130)
        self.tree_students.column("age", width=45, anchor="center")
        self.tree_students.column("gender", width=65, anchor="center")
        self.tree_students.column("course", width=90)
        self.tree_students.column("dept", width=150)
        self.tree_students.column("year", width=80, anchor="center")
        self.tree_students.column("email", width=150)
        self.tree_students.column("phone", width=95, anchor="center")
        self.tree_students.column("account", width=90, anchor="center")

        # Scrollbars
        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_students.yview)
        scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree_students.xview)
        self.tree_students.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_students.pack(fill=tk.BOTH, expand=True)

        self.tree_students.bind("<<TreeviewSelect>>", self.on_student_select)

    # =========================================================================
    # TAB 2: ANNOUNCEMENT MANAGEMENT
    # =========================================================================
    def _build_announcements_tab(self):
        paned = ttk.PanedWindow(self.tab_announcements, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Left Panel: Form
        form_frame = ttk.LabelFrame(paned, text=" Create / Edit Announcement ", padding=12)
        paned.add(form_frame, weight=1)

        ttk.Label(form_frame, text="Announcement ID (Auto):", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", pady=4)
        self.var_ann_id = tk.StringVar(value="(New)")
        lbl_id = ttk.Label(form_frame, textvariable=self.var_ann_id, foreground="#2563eb", font=("Segoe UI", 9, "bold"))
        lbl_id.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(form_frame, text="Title *:", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky="w", pady=4)
        self.var_ann_title = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.var_ann_title, width=32).grid(row=1, column=1, sticky="w", pady=4)

        ttk.Label(form_frame, text="Date (YYYY-MM-DD) *:", font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky="w", pady=4)
        self.var_ann_date = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        ttk.Entry(form_frame, textvariable=self.var_ann_date, width=32).grid(row=2, column=1, sticky="w", pady=4)

        ttk.Label(form_frame, text="Status:", font=("Segoe UI", 9, "bold")).grid(row=3, column=0, sticky="w", pady=4)
        self.var_ann_published = tk.BooleanVar(value=True)
        ttk.Checkbutton(form_frame, text="Publish immediately", variable=self.var_ann_published).grid(row=3, column=1, sticky="w", pady=4)

        ttk.Label(form_frame, text="Message *:", font=("Segoe UI", 9, "bold")).grid(row=4, column=0, sticky="nw", pady=4)
        self.txt_ann_message = tk.Text(form_frame, width=32, height=9, font=("Segoe UI", 9), wrap="word")
        self.txt_ann_message.grid(row=4, column=1, sticky="w", pady=4)

        btn_box = ttk.Frame(form_frame)
        btn_box.grid(row=5, column=0, columnspan=2, pady=12, sticky="ew")

        ttk.Button(btn_box, text="Publish / Save", style="Success.TButton", command=self.action_save_announcement).pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        ttk.Button(btn_box, text="Clear Form", style="Secondary.TButton", command=self.clear_announcement_form).pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        ttk.Button(btn_box, text="Delete", style="Danger.TButton", command=self.action_delete_announcement).pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)

        # Right Panel: Announcements Table
        table_container = ttk.Frame(paned)
        paned.add(table_container, weight=3)

        search_box = ttk.Frame(table_container, padding=6)
        search_box.pack(fill=tk.X)
        ttk.Label(search_box, text="Search Notice:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=4)
        self.var_ann_search = tk.StringVar()
        entry_ann = ttk.Entry(search_box, textvariable=self.var_ann_search, width=28)
        entry_ann.pack(side=tk.LEFT, padx=4)
        entry_ann.bind("<Return>", lambda e: self.action_search_announcements())
        ttk.Button(search_box, text="Search", style="Primary.TButton", command=self.action_search_announcements).pack(side=tk.LEFT, padx=3)
        ttk.Button(search_box, text="Reset", style="Secondary.TButton", command=self.load_announcements_table).pack(side=tk.LEFT, padx=3)

        tree_frame = ttk.Frame(table_container)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        ann_cols = ("id", "title", "date", "published", "author")
        self.tree_announcements = ttk.Treeview(tree_frame, columns=ann_cols, show="headings", selectmode="browse")
        self.tree_announcements.heading("id", text="ID")
        self.tree_announcements.heading("title", text="Title")
        self.tree_announcements.heading("date", text="Published Date")
        self.tree_announcements.heading("published", text="Is Published")
        self.tree_announcements.heading("author", text="Created By")

        self.tree_announcements.column("id", width=50, anchor="center")
        self.tree_announcements.column("title", width=250)
        self.tree_announcements.column("date", width=110, anchor="center")
        self.tree_announcements.column("published", width=100, anchor="center")
        self.tree_announcements.column("author", width=110, anchor="center")

        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_announcements.yview)
        self.tree_announcements.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_announcements.pack(fill=tk.BOTH, expand=True)

        self.tree_announcements.bind("<<TreeviewSelect>>", self.on_announcement_select)

    # =========================================================================
    # TAB 3: LEAVE MANAGEMENT
    # =========================================================================
    def _build_leaves_tab(self):
        container = ttk.Frame(self.tab_leaves, padding=8)
        container.pack(fill=tk.BOTH, expand=True)

        # Filter & Search Bar
        top_bar = ttk.Frame(container, padding=6)
        top_bar.pack(fill=tk.X)

        ttk.Label(top_bar, text="Filter Status:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=4)
        self.var_leave_filter = tk.StringVar(value="All")
        combo_filter = ttk.Combobox(
            top_bar, textvariable=self.var_leave_filter, 
            values=["All", "Pending", "Approved", "Rejected"], 
            state="readonly", width=12
        )
        combo_filter.pack(side=tk.LEFT, padx=4)
        combo_filter.bind("<<ComboboxSelected>>", lambda e: self.load_leaves_table())

        ttk.Label(top_bar, text="Search (ID / Name):", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(15, 4))
        self.var_leave_search = tk.StringVar()
        entry_lsearch = ttk.Entry(top_bar, textvariable=self.var_leave_search, width=22)
        entry_lsearch.pack(side=tk.LEFT, padx=4)
        entry_lsearch.bind("<Return>", lambda e: self.action_search_leaves())

        ttk.Button(top_bar, text="Search", style="Primary.TButton", command=self.action_search_leaves).pack(side=tk.LEFT, padx=3)
        ttk.Button(top_bar, text="Refresh All", style="Secondary.TButton", command=self.load_leaves_table).pack(side=tk.LEFT, padx=3)

        # Middle: Leaves Table
        tree_frame = ttk.Frame(container)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=6)

        l_cols = ("id", "stu_id", "name", "dept", "start", "end", "reason", "status", "submitted", "comment")
        self.tree_leaves = ttk.Treeview(tree_frame, columns=l_cols, show="headings", selectmode="browse")

        self.tree_leaves.heading("id", text="Leave #")
        self.tree_leaves.heading("stu_id", text="Student ID")
        self.tree_leaves.heading("name", text="Student Name")
        self.tree_leaves.heading("dept", text="Department")
        self.tree_leaves.heading("start", text="Start Date")
        self.tree_leaves.heading("end", text="End Date")
        self.tree_leaves.heading("reason", text="Reason")
        self.tree_leaves.heading("status", text="Status")
        self.tree_leaves.heading("submitted", text="Submitted At")
        self.tree_leaves.heading("comment", text="Admin Comment")

        self.tree_leaves.column("id", width=60, anchor="center")
        self.tree_leaves.column("stu_id", width=85, anchor="center")
        self.tree_leaves.column("name", width=120)
        self.tree_leaves.column("dept", width=130)
        self.tree_leaves.column("start", width=85, anchor="center")
        self.tree_leaves.column("end", width=85, anchor="center")
        self.tree_leaves.column("reason", width=170)
        self.tree_leaves.column("status", width=85, anchor="center")
        self.tree_leaves.column("submitted", width=130, anchor="center")
        self.tree_leaves.column("comment", width=150)

        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_leaves.yview)
        scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree_leaves.xview)
        self.tree_leaves.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_leaves.pack(fill=tk.BOTH, expand=True)

        self.tree_leaves.bind("<<TreeviewSelect>>", self.on_leave_select)

        # Bottom Action Review Panel
        review_frame = ttk.LabelFrame(container, text=" Review Selected Leave Application ", padding=10)
        review_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=6)

        ttk.Label(review_frame, text="Selected Leave Request ID:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=4)
        self.var_sel_leave_id = tk.StringVar(value="(None Selected)")
        ttk.Label(review_frame, textvariable=self.var_sel_leave_id, foreground="#2563eb", font=("Segoe UI", 9, "bold")).grid(row=0, column=1, sticky="w", padx=4)

        ttk.Label(review_frame, text="Admin Comment / Remarks:", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.var_leave_comment = tk.StringVar()
        ttk.Entry(review_frame, textvariable=self.var_leave_comment, width=50).grid(row=1, column=1, sticky="w", padx=4, pady=4)

        action_box = ttk.Frame(review_frame)
        action_box.grid(row=1, column=2, padx=15, sticky="e")

        ttk.Button(action_box, text="Approve", style="Success.TButton", command=lambda: self.action_decision_leave("Approved")).pack(side=tk.LEFT, padx=4)
        ttk.Button(action_box, text="Reject", style="Danger.TButton", command=lambda: self.action_decision_leave("Rejected")).pack(side=tk.LEFT, padx=4)
        ttk.Button(action_box, text="Delete Request", style="Secondary.TButton", command=self.action_delete_leave).pack(side=tk.LEFT, padx=4)

    # =========================================================================
    # TAB 4: ADMIN SETTINGS
    # =========================================================================
    def _build_settings_tab(self):
        container = ttk.Frame(self.tab_settings, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        card = ttk.LabelFrame(container, text=" Security Settings - Change Admin Password ", padding=20)
        card.pack(anchor="n", fill=tk.X, padx=40, pady=20)

        ttk.Label(card, text=f"Logged in Administrator: {self.admin_session['username']}", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        ttk.Label(card, text="Current Password *:").grid(row=1, column=0, sticky="w", pady=6)
        self.var_old_pwd = tk.StringVar()
        ttk.Entry(card, textvariable=self.var_old_pwd, show="*", width=30).grid(row=1, column=1, sticky="w", pady=6)

        ttk.Label(card, text="New Password *:").grid(row=2, column=0, sticky="w", pady=6)
        self.var_new_pwd = tk.StringVar()
        ttk.Entry(card, textvariable=self.var_new_pwd, show="*", width=30).grid(row=2, column=1, sticky="w", pady=6)

        ttk.Label(card, text="Confirm New Password *:").grid(row=3, column=0, sticky="w", pady=6)
        self.var_confirm_pwd = tk.StringVar()
        ttk.Entry(card, textvariable=self.var_confirm_pwd, show="*", width=30).grid(row=3, column=1, sticky="w", pady=6)

        btn_save = ttk.Button(card, text="Update Password", style="Primary.TButton", command=self.action_change_admin_pwd)
        btn_save.grid(row=4, column=0, columnspan=2, pady=15, sticky="w")

    # =========================================================================
    # LOGIC & EVENT HANDLERS: STUDENTS
    # =========================================================================
    def load_students_table(self):
        for item in self.tree_students.get_children():
            self.tree_students.delete(item)

        students = sm.get_all_students()
        for s in students:
            acc_status = s["account_username"] if s.get("account_username") else "No Account"
            self.tree_students.insert("", tk.END, values=(
                s["student_id"],
                s["name"],
                s["age"],
                s["gender"],
                s["course"],
                s["department"],
                s["year_of_study"],
                s["email"],
                s["phone"],
                acc_status
            ))

    def on_student_select(self, event):
        selected = self.tree_students.selection()
        if not selected:
            return
        item_vals = self.tree_students.item(selected[0], "values")
        if not item_vals:
            return

        student_id = item_vals[0]
        student = sm.get_student_by_id(student_id)
        if student:
            self.stu_vars["stu_id"].set(student["student_id"])
            self.stu_vars["stu_name"].set(student["name"])
            self.stu_vars["stu_age"].set(student["age"])
            self.stu_vars["stu_gender"].set(student["gender"])
            self.stu_vars["stu_course"].set(student["course"])
            self.stu_vars["stu_dept"].set(student["department"])
            self.stu_vars["stu_year"].set(student["year_of_study"])
            self.stu_vars["stu_email"].set(student["email"])
            self.stu_vars["stu_phone"].set(student["phone"])
            self.stu_vars["stu_address"].set(student["address"] or "")

            if student.get("account_username"):
                self.var_stu_user.set(student["account_username"])
            else:
                self.var_stu_user.set(student["student_id"].lower())
            self.var_stu_pwd.set("")

    def clear_student_form(self):
        for var in self.stu_vars.values():
            var.set("")
        self.stu_vars["stu_gender"].set("Male")
        self.stu_vars["stu_year"].set("1st Year")
        self.var_stu_user.set("")
        self.var_stu_pwd.set("")

    def action_add_student(self):
        data = {k: v.get() for k, v in self.stu_vars.items()}
        success, msg = sm.add_student(
            data["stu_id"], data["stu_name"], data["stu_age"], data["stu_gender"],
            data["stu_course"], data["stu_dept"], data["stu_year"], data["stu_email"],
            data["stu_phone"], data["stu_address"]
        )
        if success:
            messagebox.showinfo("Success", msg)
            self.load_students_table()
            self.clear_student_form()
        else:
            messagebox.showerror("Error", msg)

    def action_update_student(self):
        data = {k: v.get() for k, v in self.stu_vars.items()}
        if not data["stu_id"]:
            messagebox.showwarning("Warning", "Please select a student from the table to update.")
            return

        success, msg = sm.update_student(
            data["stu_id"], data["stu_name"], data["stu_age"], data["stu_gender"],
            data["stu_course"], data["stu_dept"], data["stu_year"], data["stu_email"],
            data["stu_phone"], data["stu_address"]
        )
        if success:
            messagebox.showinfo("Success", msg)
            self.load_students_table()
        else:
            messagebox.showerror("Error", msg)

    def action_delete_student(self):
        stu_id = self.stu_vars["stu_id"].get().strip()
        if not stu_id:
            messagebox.showwarning("Warning", "Please select a student from the table to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to permanently delete Student record '{stu_id}'?\n"
            "This will also delete the associated student login and leave requests."
        )
        if confirm:
            success, msg = sm.delete_student(stu_id)
            if success:
                messagebox.showinfo("Success", msg)
                self.load_students_table()
                self.clear_student_form()
            else:
                messagebox.showerror("Error", msg)

    def action_search_students(self):
        keyword = self.var_stu_search.get().strip()
        if not keyword:
            self.load_students_table()
            return
        results = sm.search_students(keyword)
        for item in self.tree_students.get_children():
            self.tree_students.delete(item)
        for s in results:
            acc_status = s["account_username"] if s.get("account_username") else "No Account"
            self.tree_students.insert("", tk.END, values=(
                s["student_id"], s["name"], s["age"], s["gender"], s["course"],
                s["department"], s["year_of_study"], s["email"], s["phone"], acc_status
            ))

    def action_create_account(self):
        stu_id = self.stu_vars["stu_id"].get().strip()
        username = self.var_stu_user.get().strip()
        password = self.var_stu_pwd.get()

        if not stu_id:
            messagebox.showwarning("Warning", "Please select or specify a Student ID first.")
            return
        if not username or not password:
            messagebox.showwarning("Warning", "Please provide both Username and Password for the student account.")
            return

        success, msg = auth.create_student_account(stu_id, username, password)
        if success:
            messagebox.showinfo("Success", msg)
            self.load_students_table()
        else:
            messagebox.showerror("Error", msg)

    def action_reset_password(self):
        stu_id = self.stu_vars["stu_id"].get().strip()
        password = self.var_stu_pwd.get()
        if not stu_id:
            messagebox.showwarning("Warning", "Please select a Student ID first.")
            return
        if not password:
            messagebox.showwarning("Warning", "Please enter a new password in the password field to reset.")
            return

        success, msg = auth.reset_student_password(stu_id, password)
        if success:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)

    # =========================================================================
    # LOGIC & EVENT HANDLERS: ANNOUNCEMENTS
    # =========================================================================
    def load_announcements_table(self):
        for item in self.tree_announcements.get_children():
            self.tree_announcements.delete(item)

        announcements = am.get_all_announcements()
        for a in announcements:
            pub_text = "Yes" if a["is_published"] else "Draft (No)"
            self.tree_announcements.insert("", tk.END, values=(
                a["announcement_id"],
                a["title"],
                str(a["published_at"]),
                pub_text,
                a["author"] or "Admin"
            ))

    def on_announcement_select(self, event):
        selected = self.tree_announcements.selection()
        if not selected:
            return
        vals = self.tree_announcements.item(selected[0], "values")
        if not vals:
            return
        ann_id = vals[0]
        # Query full record to get complete message
        query = "SELECT * FROM announcements WHERE announcement_id = %s"
        record = am.fetch_one(query, (ann_id,))
        if record:
            self.var_ann_id.set(str(record["announcement_id"]))
            self.var_ann_title.set(record["title"])
            self.var_ann_date.set(str(record["published_at"]))
            self.var_ann_published.set(bool(record["is_published"]))
            self.txt_ann_message.delete("1.0", tk.END)
            self.txt_ann_message.insert("1.0", record["message"])

    def clear_announcement_form(self):
        self.var_ann_id.set("(New)")
        self.var_ann_title.set("")
        self.var_ann_date.set(date.today().strftime("%Y-%m-%d"))
        self.var_ann_published.set(True)
        self.txt_ann_message.delete("1.0", tk.END)

    def action_save_announcement(self):
        title = self.var_ann_title.get().strip()
        pub_date = self.var_ann_date.get().strip()
        is_pub = self.var_ann_published.get()
        message = self.txt_ann_message.get("1.0", tk.END).strip()
        current_id = self.var_ann_id.get()

        if current_id == "(New)":
            success, msg = am.create_announcement(
                title=title,
                message=message,
                published_at=pub_date,
                created_by=self.admin_session.get("admin_id"),
                is_published=is_pub
            )
        else:
            success, msg = am.update_announcement(
                announcement_id=int(current_id),
                title=title,
                message=message,
                published_at=pub_date,
                is_published=is_pub
            )

        if success:
            messagebox.showinfo("Success", msg)
            self.load_announcements_table()
            self.clear_announcement_form()
        else:
            messagebox.showerror("Error", msg)

    def action_delete_announcement(self):
        current_id = self.var_ann_id.get()
        if current_id == "(New)":
            messagebox.showwarning("Warning", "Please select an announcement from the table to delete.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete announcement #{current_id}?")
        if confirm:
            success, msg = am.delete_announcement(int(current_id))
            if success:
                messagebox.showinfo("Success", msg)
                self.load_announcements_table()
                self.clear_announcement_form()
            else:
                messagebox.showerror("Error", msg)

    def action_search_announcements(self):
        kw = self.var_ann_search.get().strip()
        if not kw:
            self.load_announcements_table()
            return
        results = am.search_announcements(kw)
        for item in self.tree_announcements.get_children():
            self.tree_announcements.delete(item)
        for a in results:
            pub_text = "Yes" if a["is_published"] else "Draft (No)"
            self.tree_announcements.insert("", tk.END, values=(
                a["announcement_id"], a["title"], str(a["published_at"]), pub_text, a["author"] or "Admin"
            ))

    # =========================================================================
    # LOGIC & EVENT HANDLERS: LEAVES
    # =========================================================================
    def load_leaves_table(self):
        for item in self.tree_leaves.get_children():
            self.tree_leaves.delete(item)

        filter_val = self.var_leave_filter.get()
        leaves = lm.get_all_leave_requests(status_filter=filter_val)
        for l in leaves:
            self.tree_leaves.insert("", tk.END, values=(
                l["leave_id"],
                l["student_id"],
                l["student_name"],
                l["department"],
                str(l["start_date"]),
                str(l["end_date"]),
                l["reason"],
                l["status"],
                str(l["submitted_at"])[:16],
                l["admin_comment"] or ""
            ))

    def on_leave_select(self, event):
        selected = self.tree_leaves.selection()
        if not selected:
            return
        vals = self.tree_leaves.item(selected[0], "values")
        if not vals:
            return
        self.var_sel_leave_id.set(str(vals[0]))
        self.var_leave_comment.set(vals[9] if len(vals) > 9 else "")

    def action_decision_leave(self, status):
        leave_id_str = self.var_sel_leave_id.get()
        if leave_id_str == "(None Selected)":
            messagebox.showwarning("Warning", "Please select a leave request from the table to review.")
            return

        comment = self.var_leave_comment.get().strip()
        success, msg = lm.review_leave_request(
            leave_id=int(leave_id_str),
            status=status,
            admin_comment=comment,
            reviewed_by=self.admin_session.get("admin_id")
        )
        if success:
            messagebox.showinfo("Success", msg)
            self.load_leaves_table()
            self.var_sel_leave_id.set("(None Selected)")
            self.var_leave_comment.set("")
        else:
            messagebox.showerror("Error", msg)

    def action_delete_leave(self):
        leave_id_str = self.var_sel_leave_id.get()
        if leave_id_str == "(None Selected)":
            messagebox.showwarning("Warning", "Please select a leave request to delete.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete leave request #{leave_id_str}?")
        if confirm:
            success, msg = lm.delete_leave_request(int(leave_id_str))
            if success:
                messagebox.showinfo("Success", msg)
                self.load_leaves_table()
                self.var_sel_leave_id.set("(None Selected)")
                self.var_leave_comment.set("")
            else:
                messagebox.showerror("Error", msg)

    def action_search_leaves(self):
        kw = self.var_leave_search.get().strip()
        if not kw:
            self.load_leaves_table()
            return
        results = lm.search_leave_requests(kw)
        for item in self.tree_leaves.get_children():
            self.tree_leaves.delete(item)
        for l in results:
            self.tree_leaves.insert("", tk.END, values=(
                l["leave_id"], l["student_id"], l["student_name"], l["department"],
                str(l["start_date"]), str(l["end_date"]), l["reason"], l["status"],
                str(l["submitted_at"])[:16], l["admin_comment"] or ""
            ))

    # =========================================================================
    # LOGIC & EVENT HANDLERS: SETTINGS
    # =========================================================================
    def action_change_admin_pwd(self):
        old_p = self.var_old_pwd.get()
        new_p = self.var_new_pwd.get()
        confirm_p = self.var_confirm_pwd.get()

        if not old_p or not new_p:
            messagebox.showwarning("Warning", "Please fill in all password fields.")
            return
        if new_p != confirm_p:
            messagebox.showerror("Error", "New Password and Confirmation do not match.")
            return

        success, msg = auth.change_admin_password(self.admin_session["admin_id"], old_p, new_p)
        if success:
            messagebox.showinfo("Success", msg)
            self.var_old_pwd.set("")
            self.var_new_pwd.set("")
            self.var_confirm_pwd.set("")
        else:
            messagebox.showerror("Error", msg)

    # =========================================================================
    # GLOBAL HELPERS
    # =========================================================================
    def load_all_data(self):
        self.load_students_table()
        self.load_announcements_table()
        self.load_leaves_table()

    def handle_logout(self):
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to log out of the Admin Portal?"):
            self.on_logout_callback()
