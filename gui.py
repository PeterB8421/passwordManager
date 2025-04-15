import tkinter as tk
import pass_man

from tkinter import ttk, messagebox
from pass_man import PasswordManager

COLOR_SUCCESS = "lightgreen"
COLOR_INFO = "lightblue"
COLOR_ERROR = "red"

INPUT_WIDTH = 50

class PasswordManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Manager")

        self.option_add("*Font", "Arial 12")
        style = ttk.Style(self)
        style.configure(".", font=("Arial", 12))

        # Center the window a bit (for aesthetics)
        self.geometry("1200x800")

        self.pm = PasswordManager()

        # Create frames for "login" and "main screen"
        self.login_frame = LoginFrame(self)
        self.main_frame = MainScreenFrame(self)
        self.add_frame = AddPasswordFrame(self)
        self.edit_frame = EditPasswordFrame(self)
        self.generator_frame = PasswordGeneratorFrame(self)

        self.current_frame = self.login_frame

        # Show the login frame first
        self.login_frame.pack(fill="both", expand=True)

    def show_main_screen(self):
        """Hide the current frame and show the main screen."""
        self.current_frame.pack_forget()
        self.current_frame = self.main_frame
        self.main_frame.refresh()
        self.current_frame.pack(fill="both", expand=True)

    def show_login_screen(self):
        """Hide the current frame and show the login frame again."""
        self.current_frame.pack_forget()
        self.current_frame = self.login_frame
        self.login_frame.entry_password.bind("<Return>", self.login_frame.check_password)
        self.login_frame.hide_policy()
        self.current_frame.pack(fill="both", expand=True)

    def show_add_screen(self):
        """Hide the current frame and show the add screen again."""
        self.current_frame.pack_forget()
        self.current_frame = self.add_frame
        self.current_frame.pack(fill="both", expand=True)

    def show_edit_screen(self, record_id):
        """
        Hide the current frame, show the edit frame, and load data for record_id.
        """
        self.current_frame.pack_forget()
        self.current_frame = self.edit_frame
        self.edit_frame.pack(fill="both", expand=True)
        self.edit_frame.load_record(record_id)

    def show_generator_screen(self):
        """Hide the current frame and show the generator screen again."""
        self.current_frame.pack_forget()
        self.current_frame = self.generator_frame
        self.current_frame.pack(fill="both", expand=True)


def show_temporary_popup(root, message, color, duration_ms=2000):
    """Small temporary popup for displaying messages."""
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
        if self.master.pm.is_set:
            label_text = "Enter Master Password:"
            btn_text = "Login"
        else:
            label_text = "Create Master Password:"
            btn_text = "Create"
        self.label_instructions = tk.Label(self, text=label_text)

        self.entry_password = tk.Entry(self, show="*", width=INPUT_WIDTH)
        self.entry_password.bind("<Return>", self.check_password)
        self.entry_password.focus()
        self.button_submit = tk.Button(self, text=btn_text, command=self.check_password)

        # Layout
        self.label_instructions.pack(pady=10)
        self.entry_password.pack(pady=5)
        self.button_submit.pack(pady=5)
        self.label_requirements = None
        # If master password is not yet set, display requirements
        if not self.master.pm.is_set:
            requirements_text = (
                "Password must be at least 8 characters.\n"
                "Password must contain uppercase and lowercase characters.\n"
                "Password must contain at least one special symbol: @$!%*?&#"
            )
            self.label_requirements = tk.Label(self, text=requirements_text, fg="black")
            self.label_requirements.pack(pady=(0, 10))

    def check_password(self, event=None):
        """Check if the entered password is correct; if so, show main screen."""
        entered_password = self.entry_password.get()
        self.entry_password.delete(0, 'end')
        if not self.master.pm.is_set:
            if not self.master.pm.setup(entered_password):
                show_temporary_popup(self, "Weak password: The password provided is not strong enough!", COLOR_ERROR)
            else:
                self.master.show_main_screen()
        else:
            if self.master.pm.authenticate(entered_password):
                show_temporary_popup(self, "Login successful!", COLOR_SUCCESS)
                self.entry_password.unbind("<Return>")

                self.master.show_main_screen()
            else:
                show_temporary_popup(self, "Login failed!", COLOR_ERROR)

    def hide_policy(self):
        if self.label_requirements is not None:
            self.label_requirements.pack_forget()


class AddPasswordFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master  # Reference to the main application (PasswordManagerApp)

        # Title / Instructions
        label_title = tk.Label(self, text="Add New Password", font=("Arial", 14, "bold"))
        label_title.grid(row=0, column=0, columnspan=2, pady=10)

        # Domain Field
        tk.Label(self, text="Domain:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_domain = tk.Entry(self, width=INPUT_WIDTH)
        self.entry_domain.grid(row=1, column=1, padx=5, pady=5)

        # Username Field
        tk.Label(self, text="Username:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_username = tk.Entry(self, width=INPUT_WIDTH)
        self.entry_username.grid(row=2, column=1, padx=5, pady=5)

        # Password Field
        tk.Label(self, text="Password:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_password = tk.Entry(self, show="*", width=INPUT_WIDTH)  # masked
        self.entry_password.grid(row=3, column=1, padx=5, pady=5)

        # Note Field
        tk.Label(self, text="Note:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.entry_note = tk.Entry(self, width=INPUT_WIDTH)
        self.entry_note.grid(row=4, column=1, padx=5, pady=5)

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        btn_save = tk.Button(button_frame, text="Save", command=self.save_password)
        btn_save.pack(side="left", padx=5)

        btn_cancel = tk.Button(button_frame, text="Cancel", command=self.cancel)
        btn_cancel.pack(side="left", padx=5)

    def save_password(self):
        """Gather data from fields and add it to the password database."""
        domain = self.entry_domain.get()
        username = self.entry_username.get()
        password = self.entry_password.get()
        note = self.entry_note.get()

        if not domain or not username or not password:
            messagebox.showwarning("Warning", "Please fill in Domain, Username, and Password.")
            return

        self.master.pm.add(domain, username, password, note)

        show_temporary_popup(self, "Password saved!", COLOR_SUCCESS)

        self.entry_domain.delete(0, 'end')
        self.entry_username.delete(0, 'end')
        self.entry_password.delete(0, 'end')
        self.entry_note.delete(0, 'end')
        self.master.show_main_screen()

    def cancel(self):
        """Return to the main screen without saving."""
        self.entry_domain.delete(0, 'end')
        self.entry_username.delete(0, 'end')
        self.entry_password.delete(0, 'end')
        self.entry_note.delete(0, 'end')
        self.master.show_main_screen()


class EditPasswordFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.selected_id = None  # Will hold the ID of the record being edited

        label_title = tk.Label(self, text="Edit Password Entry", font=("Arial", 14, "bold"))
        label_title.grid(row=0, column=0, columnspan=2, pady=10)

        # Domain
        tk.Label(self, text="Domain:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_domain = tk.Entry(self, width=INPUT_WIDTH)
        self.entry_domain.grid(row=1, column=1, padx=5, pady=5)

        # Username
        tk.Label(self, text="Username:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_username = tk.Entry(self, width=INPUT_WIDTH)
        self.entry_username.grid(row=2, column=1, padx=5, pady=5)

        # Password
        tk.Label(self, text="Password:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_password = tk.Entry(self, show="*", width=INPUT_WIDTH)
        self.entry_password.grid(row=3, column=1, padx=5, pady=5)

        # Button to toggle password visibility
        self.show_password_btn = tk.Button(self, text="Show", command=self.toggle_password)
        self.show_password_btn.grid(row=3, column=2, padx=5, pady=5)

        # Note
        tk.Label(self, text="Note:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.entry_note = tk.Entry(self, width=INPUT_WIDTH)
        self.entry_note.grid(row=4, column=1, padx=5, pady=5)

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        btn_save = tk.Button(button_frame, text="Save Changes", command=self.save_changes)
        btn_save.pack(side="left", padx=5)

        btn_copy = tk.Button(button_frame, text="Copy Password", command=self.copy_password)
        btn_copy.pack(side="left", padx=5)

        btn_delete = tk.Button(button_frame, text="Delete Entry", command=self.delete_entry)
        btn_delete.pack(side="left", padx=5)

        btn_cancel = tk.Button(button_frame, text="Back", command=self.cancel)
        btn_cancel.pack(side="left", padx=5)

    def load_record(self, record_id):
        """
        Called by the main app when we navigate to this frame.
        Grabs the data from the manager, fills in the form.
        """
        self.selected_id = record_id
        record = self.master.pm.get_by_id(record_id)  # you need a method that returns (id, domain, user, pwd, note)

        if record is None:
            messagebox.showerror("Error", "Record not found.")
            return

        _, domain, username, password, note = record

        # Fill in entries
        self.entry_domain.delete(0, tk.END)
        self.entry_domain.insert(0, domain)

        self.entry_username.delete(0, tk.END)
        self.entry_username.insert(0, username)

        if password is not None:
            self.entry_password.delete(0, tk.END)
            self.entry_password.insert(0, password)
        else:
            show_temporary_popup(self, "Error decrypting password", COLOR_ERROR)

        self.entry_note.delete(0, tk.END)
        self.entry_note.insert(0, note)

    def save_changes(self):
        """Save any edits back to the database."""
        domain = self.entry_domain.get()
        username = self.entry_username.get()
        password = self.entry_password.get()
        note = self.entry_note.get()

        if not domain or not username or not password:
            messagebox.showwarning("Warning", "Please fill required fields.")
            return

        success = self.master.pm.update_by_id(self.selected_id, domain, username, password, note)
        if success:
            show_temporary_popup(self, "Changes saved!", COLOR_SUCCESS)
            self.master.show_main_screen()  # go back
        else:
            show_temporary_popup(self, "Error saving changes", COLOR_ERROR)

    def copy_password(self):
        """Copy the current password to clipboard."""
        password = self.entry_password.get()
        if password:
            self.clipboard_clear()
            self.clipboard_append(password)
            show_temporary_popup(self, "Password copied!", COLOR_INFO)

    def delete_entry(self):
        """Delete this record from the database."""
        pass
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this record?")
        if confirm:
            self.master.pm.delete_by_id(self.selected_id)
            show_temporary_popup(self, "Password deleted!", COLOR_SUCCESS)
            self.master.show_main_screen()

    def cancel(self):
        """Return to the main screen without saving."""
        self.master.show_main_screen()

    def toggle_password(self):
        """
        Toggle between showing and hiding the password text in 'entry_password'.
        """
        current_show = self.entry_password.cget("show")
        if current_show == "*":
            # It's currently hidden; show it
            self.entry_password.config(show="")
            self.show_password_btn.config(text="Hide")
        else:
            # It's currently shown; hide it
            self.entry_password.config(show="*")
            self.show_password_btn.config(text="Show")


class PasswordGeneratorFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master  # reference to your main application
        self.generated_password = ""

        # Title
        label_title = tk.Label(self, text="Password Generator", font=("Arial", 14, "bold"))
        label_title.grid(row=0, column=0, columnspan=2, pady=10)

        # Label + Spinbox: Password length
        tk.Label(self, text="Password Length:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.spin_length = tk.Spinbox(self, from_=8, to=64, width=5)
        self.spin_length.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.spin_length.delete(0, tk.END)
        self.spin_length.insert(0, "16")  # default length

        # Generate Button
        btn_generate = tk.Button(self, text="Generate", command=self.generate_password)
        btn_generate.grid(row=2, column=0, columnspan=2, pady=5)

        # Label to show the generated password
        tk.Label(self, text="Generated Password:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.label_password = tk.Label(self, text="", fg="blue", font=("Consolas", 10))
        self.label_password.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # Copy & Back buttons
        button_frame = tk.Frame(self)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        btn_copy = tk.Button(button_frame, text="Copy to Clipboard", command=self.copy_password)
        btn_copy.pack(side="left", padx=5)

        btn_back = tk.Button(button_frame, text="Back", command=self.go_back)
        btn_back.pack(side="left", padx=5)

    def generate_password(self):
        """Generate a random password using Python's 'secrets' for security."""
        # Get length from Spinbox
        try:
            length = int(self.spin_length.get())
        except ValueError:
            show_temporary_popup(self, "Invalid password length entered!", COLOR_ERROR)
            return

        generated = pass_man.generate_password(length)
        if generated is None:
            show_temporary_popup(self, "Password too short, minimum 8 characters long!", COLOR_ERROR)
            return
        # Generate
        self.generated_password = generated
        # Show in label
        self.label_password.config(text=self.generated_password)

    def copy_password(self):
        """Copy the current generated password to the clipboard."""
        if self.generated_password:
            self.clipboard_clear()
            self.clipboard_append(self.generated_password)
            show_temporary_popup(self, "Password copied!", COLOR_INFO)
        else:
            show_temporary_popup(self, "No password generated for copying!", COLOR_ERROR)

    def go_back(self):
        """Return to the main screen (or whichever screen)."""
        self.master.show_main_screen()


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

        self.tree = None

        bottom_frame = tk.Frame(self)
        bottom_frame.pack(side="bottom", fill="x")

        # Add password button, aligned to the right
        add_button = tk.Button(bottom_frame, text="Add password", command=self.add)
        add_button.pack(side="right", padx=10, pady=10)

        gen_btn = tk.Button(bottom_frame, text="Generator", command=self.generator)
        gen_btn.pack(side="right", padx=10, pady=10)

        self.refresh()

    def refresh(self):
        """Refresh the Treeview with the current database rows."""
        # Clear any old tree if we previously created it
        if self.tree:
            self.tree.pack_forget()
            self.tree.destroy()

        rows = self.master.pm.get_all_passwords()
        if not rows:
            empty_label = tk.Label(self, text="The database is empty")
            empty_label.pack()
        else:
            self.tree = ttk.Treeview(
                self,
                columns=("Domain", "Username", "Note", "Action"),
                show="headings",
            )
            self.tree.heading("Domain", text="Domain")
            self.tree.heading("Username", text="Username")
            self.tree.heading("Note", text="Note")
            self.tree.heading("Action", text="Action")

            for col in ("Domain", "Username", "Note", "Action"):
                self.tree.column(col, width=120, anchor="w", stretch=True)

            # Insert rows
            # Each row is (id, domain, username, password, note)
            for row in rows:
                row_id, domain, username, pwd, salt, nonce, tag, note = row
                # Store row_id in the "tags" or item dictionary for easy retrieval
                self.tree.insert(
                    "",
                    tk.END,
                    values=(domain, username, note, "Edit/Copy/Show/Delete"),
                    tags=(str(row_id),)  # store ID as a tag
                )

            self.tree.pack(fill="both", expand=True)

            # Bind click on the tree
            self.tree.bind("<ButtonRelease-1>", self.on_tree_click)

    def on_tree_click(self, event):
        """Handle a click on the Treeview to see if the user clicked the 'Edit' column."""
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.tree.identify_column(event.x)  # '#1', '#2', '#3', '#4'
        row_id = self.tree.identify_row(event.y)

        if not row_id:
            return

        item = self.tree.item(row_id)
        # The tag assigned that holds the DB row's ID
        record_tags = item["tags"]  # e.g. ('2',)
        if record_tags:
            record_id = int(record_tags[0])  # convert to int
            self.edit_record(record_id)

    def edit_record(self, record_id):
        self.master.show_edit_screen(record_id)

    def logout(self):
        self.master.pm.logout()
        show_temporary_popup(self, "Logout successful!", COLOR_SUCCESS)
        self.master.show_login_screen()

    def add(self):
        self.master.show_add_screen()

    def generator(self):
        self.master.show_generator_screen()


if __name__ == "__main__":
    app = PasswordManagerApp()
    app.mainloop()
