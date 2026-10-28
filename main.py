"""
main.py - Application Entry Point and Screen Navigation

Coordinates the launch of the Student Management System:
1. Validates and initializes MySQL database connection and tables.
2. Initializes the default salted admin account (NATARAJAN / NATARAJAN) on first run.
3. Provides a modern Welcome Portal with dedicated navigation to:
   - Admin Login Screen
   - Student Login Screen
   - Database Configuration Settings Dialog
4. Seamlessly navigates to Admin Dashboard and Student Dashboard upon authentication.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json

import database as db
import auth
from admin_dashboard import AdminDashboardWindow
from student_dashboard import StudentDashboardWindow


class DBConfigDialog(tk.Toplevel):
    """Dialog allowing users/beginners to configure MySQL credentials easily."""
    def __init__(self, parent, on_saved_callback):
        super().__init__(parent)
        self.title("MySQL Database Connection Settings")
        self.geometry("450x360")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.on_saved_callback = on_saved_callback
        config = db.load_db_config()

        ttk.Label(self, text="Configure MySQL Connection", font=("Segoe UI", 12, "bold")).pack(pady=10)

        form_frame = ttk.Frame(self, padding=15)
        form_frame.pack(fill=tk.BOTH, expand=True)

        fields = [
            ("Host:", "host", config.get("host", "localhost")),
            ("Port:", "port", str(config.get("port", 3306))),
            ("Database:", "database", config.get("database", "student_management")),
            ("User:", "user", config.get("user", "root")),
            ("Password:", "password", config.get("password", "root"))
        ]

        self.entries = {}
        for idx, (label_txt, key, def_val) in enumerate(fields):
            ttk.Label(form_frame, text=label_txt, font=("Segoe UI", 9, "bold")).grid(row=idx, column=0, sticky="w", pady=5)
            var = tk.StringVar(value=def_val)
            show_char = "*" if key == "password" else ""
            ent = ttk.Entry(form_frame, textvariable=var, width=28, show=show_char)
            ent.grid(row=idx, column=1, sticky="w", pady=5, padx=10)
            self.entries[key] = var

        btn_box = ttk.Frame(self, padding=10)
        btn_box.pack(fill=tk.X)

        ttk.Button(btn_box, text="Test & Save", style="Primary.TButton", command=self.save_and_test).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_box, text="Cancel", style="Secondary.TButton", command=self.destroy).pack(side=tk.RIGHT, padx=5)

    def save_and_test(self):
        new_config = {
            "host": self.entries["host"].get().strip(),
            "port": int(self.entries["port"].get().strip() or 3306),
            "database": self.entries["database"].get().strip(),
            "user": self.entries["user"].get().strip(),
            "password": self.entries["password"].get()
        }
        db.save_db_config(new_config)
        ok, msg = db.test_connection()
        if ok:
            messagebox.showinfo("Success", "MySQL connection established successfully!\nSettings saved.")
            if self.on_saved_callback:
                self.on_saved_callback()
            self.destroy()
        else:
            messagebox.showerror("Connection Failed", f"Could not connect with these settings:\n{msg}")


class StudentManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("820x600")
        self.root.minsize(780, 560)
        self.root.configure(bg="#0f172a")

        self._apply_global_styles()

        # Main active container frame
        self.container = ttk.Frame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Initialize DB and check connection
        self.check_and_init_db()

        # Show initial Welcome screen
        self.show_welcome_screen()

    def _apply_global_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("WelcomeCard.TFrame", background="#ffffff")
        style.configure("WelcomeTitle.TLabel", background="#ffffff", foreground="#0f172a", font=("Segoe UI", 22, "bold"))
        style.configure("WelcomeSubtitle.TLabel", background="#ffffff", foreground="#64748b", font=("Segoe UI", 11))

        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), background="#2563eb", foreground="#ffffff", padding=8)
        style.map("Primary.TButton", background=[("active", "#1d4ed8")])

        style.configure("Success.TButton", font=("Segoe UI", 10, "bold"), background="#16a34a", foreground="#ffffff", padding=8)
        style.map("Success.TButton", background=[("active", "#15803d")])

        style.configure("Secondary.TButton", font=("Segoe UI", 10), background="#64748b", foreground="#ffffff", padding=6)
        style.map("Secondary.TButton", background=[("active", "#475569")])

        style.configure("Danger.TButton", font=("Segoe UI", 10, "bold"), background="#dc2626", foreground="#ffffff", padding=6)
        style.map("Danger.TButton", background=[("active", "#b91c1c")])

    def check_and_init_db(self):
        """Verify database connectivity and auto-initialize tables and default admin."""
        ok, msg = db.test_connection()
        if not ok:
            # Try to run schema if database doesn't exist yet
            db.initialize_database()
            ok, msg = db.test_connection()

        if ok:
            auth.initialize_admin()
        else:
            retry = messagebox.askyesno(
                "Database Connection Error",
                f"Unable to connect to MySQL Server.\n\nError details: {msg}\n\n"
                "Would you like to configure your MySQL connection settings now?"
            )
            if retry:
                DBConfigDialog(self.root, on_saved_callback=self.on_db_configured)

    def on_db_configured(self):
        db.initialize_database()
        auth.initialize_admin()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # =========================================================================
    # SCREEN 1: WELCOME SCREEN
    # =========================================================================
    def show_welcome_screen(self):
        self.clear_container()
        self.root.title("Student Management System - Welcome")
        self.root.geometry("820x600")
        self.root.minsize(780, 560)

        wrapper = tk.Frame(self.container, bg="#0f172a")
        wrapper.pack(fill=tk.BOTH, expand=True)

        card = tk.Frame(wrapper, bg="#ffffff", padx=40, pady=35, bd=1, relief="ridge")
        card.place(relx=0.5, rely=0.5, anchor="center", width=540, height=420)

        # Logo / Badge Title
        lbl_badge = tk.Label(card, text="🎓", font=("Segoe UI Emoji", 42), bg="#ffffff")
        lbl_badge.pack(pady=(0, 5))

        lbl_title = tk.Label(card, text="STUDENT MANAGEMENT", font=("Segoe UI", 18, "bold"), fg="#0f172a", bg="#ffffff")
        lbl_title.pack()

        lbl_sub = tk.Label(card, text="Advanced Desktop Information System", font=("Segoe UI", 10), fg="#64748b", bg="#ffffff")
        lbl_sub.pack(pady=(2, 25))

        lbl_prompt = tk.Label(card, text="Select your portal to continue:", font=("Segoe UI", 10, "bold"), fg="#334155", bg="#ffffff")
        lbl_prompt.pack(pady=(0, 15))

        # Admin Portal Button
        btn_admin = tk.Button(
            card, text="🔑  Administrator Portal", font=("Segoe UI", 11, "bold"),
            bg="#1e293b", fg="#ffffff", activebackground="#0f172a", activeforeground="#ffffff",
            cursor="hand2", bd=0, relief="flat", padx=10, pady=10,
            command=self.show_admin_login_screen
        )
        btn_admin.pack(fill=tk.X, pady=6)

        # Student Portal Button
        btn_student = tk.Button(
            card, text="👨‍🎓  Student Portal", font=("Segoe UI", 11, "bold"),
            bg="#0284c7", fg="#ffffff", activebackground="#0369a1", activeforeground="#ffffff",
            cursor="hand2", bd=0, relief="flat", padx=10, pady=10,
            command=self.show_student_login_screen
        )
        btn_student.pack(fill=tk.X, pady=6)

    # =========================================================================
    # SCREEN 2: ADMIN LOGIN SCREEN
    # =========================================================================
    def show_admin_login_screen(self):
        self.clear_container()
        self.root.title("Administrator Login - Student Management System")

        wrapper = tk.Frame(self.container, bg="#0f172a")
        wrapper.pack(fill=tk.BOTH, expand=True)

        card = tk.Frame(wrapper, bg="#ffffff", padx=40, pady=30, bd=1, relief="ridge")
        card.place(relx=0.5, rely=0.5, anchor="center", width=480, height=470)

        tk.Label(card, text="🔑", font=("Segoe UI Emoji", 32), bg="#ffffff").pack()
        tk.Label(card, text="Admin Authentication", font=("Segoe UI", 16, "bold"), fg="#1e293b", bg="#ffffff").pack(pady=(0, 2))
        tk.Label(card, text="Default Admin ID: NATARAJAN", font=("Segoe UI", 9, "italic"), fg="#64748b", bg="#ffffff").pack(pady=(0, 20))

        # Inputs
        form = tk.Frame(card, bg="#ffffff")
        form.pack(fill=tk.X)

        tk.Label(form, text="Admin Username:", font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#334155").pack(anchor="w", pady=(5, 2))
        var_user = tk.StringVar(value="NATARAJAN")
        entry_user = ttk.Entry(form, textvariable=var_user, font=("Segoe UI", 10), width=30)
        entry_user.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Password:", font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#334155").pack(anchor="w", pady=(5, 2))
        var_pwd = tk.StringVar()
        entry_pwd = ttk.Entry(form, textvariable=var_pwd, show="*", font=("Segoe UI", 10), width=30)
        entry_pwd.pack(fill=tk.X, pady=(0, 5))

        var_show = tk.BooleanVar(value=False)
        def toggle_pwd():
            entry_pwd.config(show="" if var_show.get() else "*")

        cb_show = tk.Checkbutton(form, text="Show Password", variable=var_show, command=toggle_pwd, bg="#ffffff", activebackground="#ffffff")
        cb_show.pack(anchor="w", pady=(0, 15))

        def handle_admin_login():
            u = var_user.get().strip()
            p = var_pwd.get()
            if not u or not p:
                messagebox.showwarning("Input Required", "Please enter both Admin Username and Password.")
                return

            admin_data = auth.authenticate_admin(u, p)
            if admin_data:
                self.launch_admin_dashboard(admin_data)
            else:
                messagebox.showerror("Authentication Failed", "Invalid Admin Username or Password.")

        # Bind Enter key
        entry_pwd.bind("<Return>", lambda e: handle_admin_login())

        btn_login = tk.Button(
            card, text="Login as Administrator", font=("Segoe UI", 10, "bold"),
            bg="#2563eb", fg="#ffffff", activebackground="#1d4ed8", activeforeground="#ffffff",
            cursor="hand2", bd=0, relief="flat", pady=8, command=handle_admin_login
        )
        btn_login.pack(fill=tk.X, pady=(5, 10))

        btn_back = tk.Button(
            card, text="← Back to Welcome Portal", font=("Segoe UI", 9),
            bg="#ffffff", fg="#475569", activebackground="#f1f5f9", activeforeground="#0f172a",
            cursor="hand2", bd=0, relief="flat", command=self.show_welcome_screen
        )
        btn_back.pack()

    # =========================================================================
    # SCREEN 3: STUDENT LOGIN SCREEN
    # =========================================================================
    def show_student_login_screen(self):
        self.clear_container()
        self.root.title("Student Login - Student Management System")

        wrapper = tk.Frame(self.container, bg="#0f172a")
        wrapper.pack(fill=tk.BOTH, expand=True)

        card = tk.Frame(wrapper, bg="#ffffff", padx=40, pady=30, bd=1, relief="ridge")
        card.place(relx=0.5, rely=0.5, anchor="center", width=480, height=470)

        tk.Label(card, text="👨‍🎓", font=("Segoe UI Emoji", 32), bg="#ffffff").pack()
        tk.Label(card, text="Student Authentication", font=("Segoe UI", 16, "bold"), fg="#0f172a", bg="#ffffff").pack(pady=(0, 2))
        tk.Label(card, text="Enter your assigned student credentials", font=("Segoe UI", 9, "italic"), fg="#64748b", bg="#ffffff").pack(pady=(0, 20))

        # Inputs
        form = tk.Frame(card, bg="#ffffff")
        form.pack(fill=tk.X)

        tk.Label(form, text="Student Login ID / Username:", font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#334155").pack(anchor="w", pady=(5, 2))
        var_user = tk.StringVar()
        entry_user = ttk.Entry(form, textvariable=var_user, font=("Segoe UI", 10), width=30)
        entry_user.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Password:", font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#334155").pack(anchor="w", pady=(5, 2))
        var_pwd = tk.StringVar()
        entry_pwd = ttk.Entry(form, textvariable=var_pwd, show="*", font=("Segoe UI", 10), width=30)
        entry_pwd.pack(fill=tk.X, pady=(0, 5))

        var_show = tk.BooleanVar(value=False)
        def toggle_pwd():
            entry_pwd.config(show="" if var_show.get() else "*")

        cb_show = tk.Checkbutton(form, text="Show Password", variable=var_show, command=toggle_pwd, bg="#ffffff", activebackground="#ffffff")
        cb_show.pack(anchor="w", pady=(0, 15))

        def handle_student_login():
            u = var_user.get().strip()
            p = var_pwd.get()
            if not u or not p:
                messagebox.showwarning("Input Required", "Please enter both Student Username and Password.")
                return

            res = auth.authenticate_student(u, p)
            if res:
                if "error" in res:
                    messagebox.showerror("Account Notice", res["error"])
                else:
                    self.launch_student_dashboard(res)
            else:
                messagebox.showerror("Authentication Failed", "Invalid Student Username or Password.")

        entry_pwd.bind("<Return>", lambda e: handle_student_login())

        btn_login = tk.Button(
            card, text="Login to Student Portal", font=("Segoe UI", 10, "bold"),
            bg="#0284c7", fg="#ffffff", activebackground="#0369a1", activeforeground="#ffffff",
            cursor="hand2", bd=0, relief="flat", pady=8, command=handle_student_login
        )
        btn_login.pack(fill=tk.X, pady=(5, 10))

        btn_back = tk.Button(
            card, text="← Back to Welcome Portal", font=("Segoe UI", 9),
            bg="#ffffff", fg="#475569", activebackground="#f1f5f9", activeforeground="#0f172a",
            cursor="hand2", bd=0, relief="flat", command=self.show_welcome_screen
        )
        btn_back.pack()

    # =========================================================================
    # DASHBOARD LAUNCHERS
    # =========================================================================
    def launch_admin_dashboard(self, admin_session):
        self.clear_container()
        AdminDashboardWindow(
            root=self.container,
            admin_session=admin_session,
            on_logout_callback=self.show_welcome_screen
        )

    def launch_student_dashboard(self, student_session):
        self.clear_container()
        StudentDashboardWindow(
            root=self.container,
            student_session=student_session,
            on_logout_callback=self.show_welcome_screen
        )


def main():
    root = tk.Tk()
    app = StudentManagementApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
