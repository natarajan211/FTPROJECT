"""
student_dashboard.py - Student GUI Interface

Provides a dedicated, secure, and restricted desktop portal for authenticated students:
1. My Profile (strictly read-only view of academic and biographical records)
2. College Announcements (read-only broadcast feed from administrators, latest first)
3. Apply for Leave (input form with date validations: end_date >= start_date)
4. My Leave History (strictly displays authenticated student's own requests and review status)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

import announcement_management as am
import leave_management as lm
import student_management as sm


class StudentDashboardWindow:
    def __init__(self, root, student_session, on_logout_callback):
        self.root = root
        self.student_session = student_session
        self.on_logout_callback = on_logout_callback

        top = self.root.winfo_toplevel()
        top.title(f"Student Portal - {self.student_session['name']} ({self.student_session['student_id']})")
        top.geometry("1100x700")
        top.minsize(980, 620)

        self._apply_styles()
        self._build_ui()
        self.load_all_data()

    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Color Palette
        bg_dark = "#0f172a"      # Deep slate
        primary = "#0284c7"      # Sky blue
        success = "#16a34a"      # Emerald green
        danger = "#dc2626"       # Crimson red

        style.configure("StudentHeader.TFrame", background=bg_dark)
        style.configure("StudentHeader.TLabel", background=bg_dark, foreground="#ffffff", font=("Segoe UI", 15, "bold"))
        style.configure("StudentHeaderSub.TLabel", background=bg_dark, foreground="#94a3b8", font=("Segoe UI", 10))

        # Notebook tabs
        style.configure("TNotebook", background="#f8fafc", tabmargins=[10, 10, 10, 0])
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[16, 8])
        style.map("TNotebook.Tab",
                  background=[("selected", "#ffffff"), ("!selected", "#e2e8f0")],
                  foreground=[("selected", primary), ("!selected", "#475569")])

        # Treeview styling
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=26, background="#ffffff")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e2e8f0", foreground="#1e293b")
        style.map("Treeview", background=[("selected", "#bae6fd")], foreground=[("selected", "#0f172a")])

        # Buttons
        style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"), background=primary, foreground="#ffffff")
        style.map("Primary.TButton", background=[("active", "#0369a1")])

        style.configure("Success.TButton", font=("Segoe UI", 9, "bold"), background=success, foreground="#ffffff")
        style.map("Success.TButton", background=[("active", "#15803d")])

        style.configure("Danger.TButton", font=("Segoe UI", 9, "bold"), background=danger, foreground="#ffffff")
        style.map("Danger.TButton", background=[("active", "#b91c1c")])

        style.configure("Secondary.TButton", font=("Segoe UI", 9), background="#64748b", foreground="#ffffff")
        style.map("Secondary.TButton", background=[("active", "#475569")])

    def _build_ui(self):
        # 1. Top Header Frame
        header = ttk.Frame(self.root, style="StudentHeader.TFrame", height=65)
        header.pack(fill=tk.X, side=tk.TOP)

        title_box = ttk.Frame(header, style="StudentHeader.TFrame")
        title_box.pack(side=tk.LEFT, padx=20, pady=10)

        lbl_title = ttk.Label(title_box, text=f"WELCOME, {self.student_session['name'].upper()}", style="StudentHeader.TLabel")
        lbl_title.pack(anchor="w")

        info_sub = f"Student ID: {self.student_session['student_id']} | Dept: {self.student_session['department']} | Course: {self.student_session['course']}"
        lbl_subtitle = ttk.Label(title_box, text=info_sub, style="StudentHeaderSub.TLabel")
        lbl_subtitle.pack(anchor="w")

        btn_logout = ttk.Button(header, text="Logout", style="Danger.TButton", command=self.handle_logout)
        btn_logout.pack(side=tk.RIGHT, padx=20, pady=15)

        # 2. Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.tab_profile = ttk.Frame(self.notebook)
        self.tab_announcements = ttk.Frame(self.notebook)
        self.tab_apply_leave = ttk.Frame(self.notebook)
        self.tab_my_leaves = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_profile, text="  My Profile  ")
        self.notebook.add(self.tab_announcements, text="  College Announcements  ")
        self.notebook.add(self.tab_apply_leave, text="  Apply for Leave  ")
        self.notebook.add(self.tab_my_leaves, text="  My Leave History  ")

        self._build_profile_tab()
        self._build_announcements_tab()
        self._build_apply_leave_tab()
        self._build_my_leaves_tab()

    # =========================================================================
    # TAB 1: MY PROFILE (READ-ONLY)
    # =========================================================================
    def _build_profile_tab(self):
        outer = ttk.Frame(self.tab_profile, padding=25)
        outer.pack(fill=tk.BOTH, expand=True)

        card = ttk.LabelFrame(outer, text=" Official Student Profile (Read-Only) ", padding=20)
        card.pack(anchor="nw", fill=tk.BOTH, expand=True)

        info_notice = ttk.Label(
            card,
            text="* Official institutional profile records are managed by the College Administration. "
                 "Students cannot modify or delete their official student records.",
            foreground="#64748b",
            font=("Segoe UI", 9, "italic")
        )
        info_notice.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        # Refresh profile info from database
        student_data = sm.get_student_by_id(self.student_session["student_id"]) or self.student_session

        profile_items = [
            ("Student ID:", student_data.get("student_id", "")),
            ("Full Name:", student_data.get("name", "")),
            ("Age:", str(student_data.get("age", ""))),
            ("Gender:", student_data.get("gender", "")),
            ("Course:", student_data.get("course", "")),
            ("Department:", student_data.get("department", "")),
            ("Year of Study:", student_data.get("year_of_study", "")),
            ("Registered Email:", student_data.get("email", "")),
            ("Contact Phone:", student_data.get("phone", "")),
            ("Permanent Address:", student_data.get("address", "") or "Not Provided"),
            ("Portal Username:", self.student_session.get("username", ""))
        ]

        for i, (label, value) in enumerate(profile_items, start=1):
            lbl_title = ttk.Label(card, text=label, font=("Segoe UI", 10, "bold"), width=20)
            lbl_title.grid(row=i, column=0, sticky="w", pady=5)

            lbl_val = ttk.Label(card, text=value, font=("Segoe UI", 10), foreground="#0f172a")
            lbl_val.grid(row=i, column=1, sticky="w", pady=5)

    # =========================================================================
    # TAB 2: ANNOUNCEMENTS (READ-ONLY, LATEST FIRST)
    # =========================================================================
    def _build_announcements_tab(self):
        container = ttk.Frame(self.tab_announcements, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        top_bar = ttk.Frame(container)
        top_bar.pack(fill=tk.X, pady=(0, 8))

        lbl = ttk.Label(top_bar, text="College Bulletins & Official Notices", font=("Segoe UI", 11, "bold"))
        lbl.pack(side=tk.LEFT)

        btn_refresh = ttk.Button(top_bar, text="Refresh Notices", style="Secondary.TButton", command=self.load_announcements)
        btn_refresh.pack(side=tk.RIGHT)

        paned = ttk.PanedWindow(container, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Upper Table
        tree_frame = ttk.Frame(paned)
        paned.add(tree_frame, weight=2)

        cols = ("id", "title", "date")
        self.tree_ann = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        self.tree_ann.heading("id", text="ID")
        self.tree_ann.heading("title", text="Notice Title")
        self.tree_ann.heading("date", text="Published Date")

        self.tree_ann.column("id", width=60, anchor="center")
        self.tree_ann.column("title", width=600)
        self.tree_ann.column("date", width=150, anchor="center")

        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_ann.yview)
        self.tree_ann.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_ann.pack(fill=tk.BOTH, expand=True)

        self.tree_ann.bind("<<TreeviewSelect>>", self.on_announcement_select)

        # Lower Detail View
        detail_frame = ttk.LabelFrame(paned, text=" Notice Message Content ", padding=10)
        paned.add(detail_frame, weight=3)

        self.txt_ann_view = tk.Text(detail_frame, font=("Segoe UI", 10), wrap="word", bg="#f8fafc", relief="flat")
        self.txt_ann_view.pack(fill=tk.BOTH, expand=True)
        self.txt_ann_view.config(state="disabled")

    # =========================================================================
    # TAB 3: APPLY FOR LEAVE
    # =========================================================================
    def _build_apply_leave_tab(self):
        container = ttk.Frame(self.tab_apply_leave, padding=25)
        container.pack(fill=tk.BOTH, expand=True)

        card = ttk.LabelFrame(container, text=" Submit Leave Application ", padding=20)
        card.pack(anchor="n", fill=tk.X, padx=30, pady=10)

        # Today's date as default
        today_str = date.today().strftime("%Y-%m-%d")

        ttk.Label(card, text="Start Date (YYYY-MM-DD) *:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", pady=8)
        self.var_leave_start = tk.StringVar(value=today_str)
        entry_start = ttk.Entry(card, textvariable=self.var_leave_start, width=28)
        entry_start.grid(row=0, column=1, sticky="w", pady=8)

        ttk.Label(card, text="End Date (YYYY-MM-DD) *:", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky="w", pady=8)
        self.var_leave_end = tk.StringVar(value=today_str)
        entry_end = ttk.Entry(card, textvariable=self.var_leave_end, width=28)
        entry_end.grid(row=1, column=1, sticky="w", pady=8)

        ttk.Label(card, text="Reason for Leave *:", font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky="nw", pady=8)
        self.txt_leave_reason = tk.Text(card, width=42, height=6, font=("Segoe UI", 9), wrap="word")
        self.txt_leave_reason.grid(row=2, column=1, sticky="w", pady=8)

        btn_box = ttk.Frame(card)
        btn_box.grid(row=3, column=0, columnspan=2, pady=15, sticky="w")

        btn_submit = ttk.Button(btn_box, text="Submit Application", style="Primary.TButton", command=self.action_submit_leave)
        btn_submit.pack(side=tk.LEFT, padx=(0, 10))

        btn_clear = ttk.Button(btn_box, text="Reset Form", style="Secondary.TButton", command=self.clear_leave_form)
        btn_clear.pack(side=tk.LEFT)

    # =========================================================================
    # TAB 4: MY LEAVE HISTORY
    # =========================================================================
    def _build_my_leaves_tab(self):
        container = ttk.Frame(self.tab_my_leaves, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        top_bar = ttk.Frame(container)
        top_bar.pack(fill=tk.X, pady=(0, 8))

        lbl = ttk.Label(top_bar, text="My Submitted Leave Applications", font=("Segoe UI", 11, "bold"))
        lbl.pack(side=tk.LEFT)

        btn_refresh = ttk.Button(top_bar, text="Refresh Status", style="Secondary.TButton", command=self.load_leave_history)
        btn_refresh.pack(side=tk.RIGHT)

        tree_frame = ttk.Frame(container)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("id", "start", "end", "reason", "submitted", "status", "comment")
        self.tree_history = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")

        self.tree_history.heading("id", text="Request ID")
        self.tree_history.heading("start", text="Start Date")
        self.tree_history.heading("end", text="End Date")
        self.tree_history.heading("reason", text="Reason")
        self.tree_history.heading("submitted", text="Submitted Date")
        self.tree_history.heading("status", text="Status")
        self.tree_history.heading("comment", text="Admin Remarks")

        self.tree_history.column("id", width=75, anchor="center")
        self.tree_history.column("start", width=95, anchor="center")
        self.tree_history.column("end", width=95, anchor="center")
        self.tree_history.column("reason", width=220)
        self.tree_history.column("submitted", width=130, anchor="center")
        self.tree_history.column("status", width=95, anchor="center")
        self.tree_history.column("comment", width=220)

        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_history.yview)
        scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree_history.xview)
        self.tree_history.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_history.pack(fill=tk.BOTH, expand=True)

    # =========================================================================
    # EVENT HANDLERS & LOGIC
    # =========================================================================
    def load_announcements(self):
        for item in self.tree_ann.get_children():
            self.tree_ann.delete(item)

        notices = am.get_published_announcements()
        for n in notices:
            self.tree_ann.insert("", tk.END, values=(n["announcement_id"], n["title"], str(n["published_at"])))

        self.txt_ann_view.config(state="normal")
        self.txt_ann_view.delete("1.0", tk.END)
        self.txt_ann_view.insert("1.0", "Select a notice from above to view its complete details.")
        self.txt_ann_view.config(state="disabled")

    def on_announcement_select(self, event):
        selected = self.tree_ann.selection()
        if not selected:
            return
        vals = self.tree_ann.item(selected[0], "values")
        if not vals:
            return

        ann_id = vals[0]
        query = "SELECT * FROM announcements WHERE announcement_id = %s"
        notice = am.fetch_one(query, (ann_id,))
        if notice:
            self.txt_ann_view.config(state="normal")
            self.txt_ann_view.delete("1.0", tk.END)
            text_body = f"TITLE: {notice['title']}\n"
            text_body += f"DATE:  {str(notice['published_at'])}\n"
            text_body += "-" * 60 + "\n\n"
            text_body += notice["message"]
            self.txt_ann_view.insert("1.0", text_body)
            self.txt_ann_view.config(state="disabled")

    def clear_leave_form(self):
        today_str = date.today().strftime("%Y-%m-%d")
        self.var_leave_start.set(today_str)
        self.var_leave_end.set(today_str)
        self.txt_leave_reason.delete("1.0", tk.END)

    def action_submit_leave(self):
        start_d = self.var_leave_start.get().strip()
        end_d = self.var_leave_end.get().strip()
        reason = self.txt_leave_reason.get("1.0", tk.END).strip()

        # Submit query using strictly the authenticated session's student_id
        student_id = self.student_session["student_id"]

        success, msg = lm.submit_leave_request(student_id, start_d, end_d, reason)
        if success:
            messagebox.showinfo("Success", msg)
            self.clear_leave_form()
            self.load_leave_history()
            # Switch to Leave History tab so student immediately sees their request
            self.notebook.select(self.tab_my_leaves)
        else:
            messagebox.showerror("Error", msg)

    def load_leave_history(self):
        for item in self.tree_history.get_children():
            self.tree_history.delete(item)

        # Strictly uses session student_id
        leaves = lm.get_student_leave_history(self.student_session["student_id"])
        for l in leaves:
            self.tree_history.insert("", tk.END, values=(
                l["leave_id"],
                str(l["start_date"]),
                str(l["end_date"]),
                l["reason"],
                str(l["submitted_at"])[:16],
                l["status"],
                l["admin_comment"] or "Pending admin review"
            ))

    def load_all_data(self):
        self.load_announcements()
        self.load_leave_history()

    def handle_logout(self):
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to log out of the Student Portal?"):
            self.on_logout_callback()
