import tkinter
import tkinter as tk
from tkinter import ttk, messagebox
from pass_man import PasswordManager

# --- Fake "database" of saved passwords (service, username, password) ---
FAKE_DB = [
    ("Email", "myemail@example.com", "email_pass123"),
    ("GitHub", "mygithubuser", "github_pass456"),
    ("Netflix", "mynetflixuser", "netflix_pass789"),
]

# Master password for demo purposes
MASTER_PASSWORD = "1234"


class PasswordManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Manager")

        # Center the window a bit (for aesthetics)
        self.geometry("400x250")

        self.pm = PasswordManager()

        # Create frames for "login" and "main screen"
        self.login_frame = LoginFrame(self)
        self.main_frame = MainScreenFrame(self)

        # Show the login frame first
        self.login_frame.pack(fill="both", expand=True)

    def show_main_screen(self):
        """Hide the login frame and show the main screen."""
        self.login_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True)

    def show_login_screen(self):
        """Hide the main frame and show the login frame again."""
        self.main_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)


def show_temporary_popup(root, message, color, duration_ms=2000):
    popup = tk.Toplevel(root)
    popup.title("")  # no title
    popup.overrideredirect(True)  # remove window borders (optional)

    # Place the popup near the main window
    x = root.winfo_rootx() + 200
    y = root.winfo_rooty()
    popup.geometry(f"+{x}+{y}")

    lbl = tk.Label(popup, text=message, fg="black", bg=color, padx=10, pady=5)
    lbl.pack()

    popup.after(duration_ms, popup.destroy)


class LoginFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        # Widgets
        self.label_instructions = tk.Label(self, text="Enter Master Password:")
        self.entry_password = tk.Entry(self, show="*")
        self.button_submit = tk.Button(self, text="Login", command=self.check_password)

        # Layout
        self.label_instructions.pack(pady=10)
        self.entry_password.pack(pady=5)
        self.button_submit.pack(pady=5)

    def check_password(self):
        """Check if the entered password is correct; if so, show main screen."""
        entered_password = self.entry_password.get()
        self.entry_password.delete(0, 'end')
        if not self.master.pm.is_set:
            if not self.master.pm.setup(entered_password):
                messagebox.showerror("Error", "There was a problem creating the master password.")
            else:
                self.master.show_main_screen()
        else:
            if self.master.pm.authenticate(entered_password):
                show_temporary_popup(self, "Login successful!", "lightgreen")
                self.master.show_main_screen()
            else:
                show_temporary_popup(self, "Login failed!", "red")


class MainScreenFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        top_frame = tk.Frame(self)
        top_frame.pack(side="top", fill="x")
        logout_btn = tk.Button(top_frame, text="Logout", command=self.logout)
        logout_btn.pack(side="left", padx=10, pady=10)

        # Label at the top
        self.label_title = tk.Label(self, text="Password database", font=("Arial", 14, "bold"))
        self.label_title.pack(pady=10)

        rows = self.master.pm.get_all_passwords()
        print(rows)
        if not rows:
            empty_label = tk.Label(self, text="The database is empty")
            empty_label.pack()
        else:
            # Create a Treeview to list passwords
            self.tree = ttk.Treeview(self, columns=("Domain", "Username", "Note", "Actions"), show="headings")
            self.tree.heading("Domain", text="Domain")
            self.tree.heading("Username", text="Username")
            self.tree.heading("Note", text="Note")
            self.tree.heading("Actions", text="Actions")

            column_names = ("Domain", "Username", "Note", "Actions")
            for col in column_names:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100, anchor="w", stretch=True)

            # Insert the fake DB data into Treeview
            # for record in FAKE_DB:
            #     self.tree.insert("", tk.END, values=record)

            self.tree.pack(fill="both", expand=True)

        bottom_frame = tk.Frame(self)
        bottom_frame.pack(side="bottom", fill="x")

        # Add password button, aligned to the right
        add_button = tk.Button(bottom_frame, text="Add password")
        add_button.pack(side="right", padx=10, pady=10)

    def logout(self):
        self.master.pm.logout()
        show_temporary_popup(self, "Logout successful!", "lightgreen")
        self.master.show_login_screen()


if __name__ == "__main__":
    app = PasswordManagerApp()
    app.mainloop()
