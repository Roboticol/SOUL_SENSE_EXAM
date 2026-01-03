import sqlite3
import tkinter as tk
from tkinter import messagebox

class SoulSenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Soul Sense EQ Test")
        self.root.geometry("600x400")
        self.username = ""
        self.age = None
        self.current_question = 0
        self.responses = []
        
        # Setup database
        self.setup_database()
        
        # Load questions
        self.load_questions()
        
        # Initialize journal
        try:
            from journal_feature import JournalFeature
            self.journal = JournalFeature(root)
            self.journal_available = True
        except ImportError:
            self.journal = None
            self.journal_available = False
        
        self.create_username_screen()

    def setup_database(self):
        self.conn = sqlite3.connect("soulsense_db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            age INTEGER,
            total_score INTEGER
        )
        """)
        self.conn.commit()

    def load_questions(self):
        self.questions = []
        try:
            with open('question_bank.txt', 'r') as f:
                all_questions = [line.strip() for line in f if line.strip()]
                self.questions = all_questions[:20]  # First 20 questions
        except FileNotFoundError:
            messagebox.showerror("Error", "question_bank.txt file not found!")
            self.root.quit()

    def create_username_screen(self):
        self.clear_screen()
        
        # Title
        title = tk.Label(self.root, text="Soul Sense EQ Test", 
                        font=("Arial", 18, "bold"), fg="blue")
        title.pack(pady=20)
        
        # Name input
        tk.Label(self.root, text="Enter Your Name:", font=("Arial", 14)).pack(pady=10)
        self.name_entry = tk.Entry(self.root, font=("Arial", 14), width=25)
        self.name_entry.pack(pady=5)
        
        # Age input
        tk.Label(self.root, text="Enter Your Age (optional):", font=("Arial", 14)).pack(pady=10)
        self.age_entry = tk.Entry(self.root, font=("Arial", 14), width=25)
        self.age_entry.pack(pady=5)
        
        # Start button
        tk.Button(self.root, text="Start Test", command=self.start_test, 
                 font=("Arial", 14), bg="green", fg="white", width=15).pack(pady=30)

    def start_test(self):
        self.username = self.name_entry.get().strip()
        age_str = self.age_entry.get().strip()
        
        if not self.username:
            messagebox.showwarning("Input Error", "Please enter your name.")
            return
        
        if age_str:
            try:
                self.age = int(age_str)
                if self.age < 1 or self.age > 120:
                    messagebox.showwarning("Input Error", "Please enter a valid age (1-120).")
                    return
            except ValueError:
                messagebox.showwarning("Input Error", "Age must be a number.")
                return
        
        self.current_question = 0
        self.responses = []
        self.show_question()

    def show_question(self):
        self.clear_screen()
        
        if self.current_question < len(self.questions):
            # Progress indicator
            progress = tk.Label(self.root, 
                              text=f"Question {self.current_question + 1} of {len(self.questions)}", 
                              font=("Arial", 12), fg="gray")
            progress.pack(pady=10)
            
            # Question text
            q_text = self.questions[self.current_question]
            question_label = tk.Label(self.root, text=q_text, 
                                    wraplength=500, font=("Arial", 14), justify="center")
            question_label.pack(pady=20)
            
            # Answer options
            self.answer_var = tk.IntVar()
            
            options_frame = tk.Frame(self.root)
            options_frame.pack(pady=20)
            
            for val, text in enumerate(["Never (1)", "Sometimes (2)", "Often (3)", "Always (4)"], start=1):
                tk.Radiobutton(options_frame, text=text, variable=self.answer_var, 
                             value=val, font=("Arial", 12)).pack(anchor="w", pady=5)
            
            # Next button
            tk.Button(self.root, text="Next", command=self.save_answer, 
                     font=("Arial", 12), bg="blue", fg="white", width=10).pack(pady=30)
        else:
            self.finish_test()

    def save_answer(self):
        ans = self.answer_var.get()
        if ans == 0:
            messagebox.showwarning("Input Error", "Please select an answer before proceeding.")
        else:
            self.responses.append(ans)
            self.current_question += 1
            self.show_question()

    def finish_test(self):
        total_score = sum(self.responses)
        
        # Store score in database
        self.cursor.execute("INSERT INTO scores (username, age, total_score) VALUES (?, ?, ?)", 
                           (self.username, self.age, total_score))
        self.conn.commit()
        
        # Determine interpretation
        if total_score >= 65:
            interpretation = "Excellent Emotional Intelligence!"
            color = "green"
        elif total_score >= 50:
            interpretation = "Good Emotional Intelligence."
            color = "blue"
        elif total_score >= 35:
            interpretation = "Average Emotional Intelligence."
            color = "orange"
        else:
            interpretation = "You may want to work on your Emotional Intelligence."
            color = "red"
        
        self.show_results(total_score, interpretation, color)

    def show_results(self, total_score, interpretation, color):
        self.clear_screen()
        
        # Results display
        tk.Label(self.root, text="Test Complete!", 
                font=("Arial", 18, "bold"), fg="blue").pack(pady=20)
        
        tk.Label(self.root, text=f"Thank you, {self.username}!", 
                font=("Arial", 16)).pack(pady=10)
        
        tk.Label(self.root, text=f"Your EQ Score: {total_score} / 80", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        tk.Label(self.root, text=interpretation, 
                font=("Arial", 14), fg=color).pack(pady=10)
        
        # Show all results in console
        self.show_all_results()
        
        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=30)
        
        if self.journal_available:
            tk.Button(button_frame, text="Open Journal", command=self.open_journal, 
                     font=("Arial", 12), bg="#2196F3", fg="white", width=12).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Take Test Again", command=self.create_username_screen, 
                 font=("Arial", 12), bg="green", fg="white", width=12).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Exit", command=self.exit_test, 
                 font=("Arial", 12), bg="red", fg="white", width=12).pack(side=tk.LEFT, padx=10)

    def show_all_results(self):
        print("\n" + "="*50)
        print("           ALL EQ TEST RESULTS")
        print("="*50)
        print(f"{'Username':<20} {'Age':<10} {'Score':<10}")
        print("-" * 50)
        
        self.cursor.execute("SELECT username, age, total_score FROM scores ORDER BY rowid DESC")
        rows = self.cursor.fetchall()
        
        for row in rows:
            age_display = str(row[1]) if row[1] is not None else "N/A"
            print(f"{row[0]:<20} {age_display:<10} {row[2]:<10}")
        
        print("="*50)

    def open_journal(self):
        if self.journal:
            self.journal.open_journal_window(self.username)
        else:
            messagebox.showinfo("Info", "Journal feature not available")

    def exit_test(self):
        self.conn.close()
        self.root.quit()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SoulSenseApp(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_test)
    root.mainloop()