import customtkinter as ctk
import threading
import time
import random

class ProgressBarExample(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Progress Bar Example")
        self.geometry("400x300")

        # Label for description
        self.label = ctk.CTkLabel(self, text="Progress of File Transmission:")
        self.label.pack(pady=10)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10, padx=20, fill='x')

        # Log area (to show the transmission status)
        self.log_text = ctk.CTkTextbox(self, height=100)
        self.log_text.pack(pady=10, padx=20, fill='both', expand=True)

        # Start button to initiate transmission
        self.start_button = ctk.CTkButton(self, text="Start Transmission", command=self.start_transmission)
        self.start_button.pack(pady=10)

    def start_transmission(self):
        # Start transmission in a separate thread
        transmission_thread = threading.Thread(target=self.transmission_process)
        transmission_thread.start()

    def transmission_process(self):
        files_to_send = ["file1.png", "file2.png", "file3.png", "file4.png", "file5.png"]
        total_files = len(files_to_send)

        for idx, file in enumerate(files_to_send, start=1):
            # Simulate actual work completion with gradual progress
            work_duration = random.uniform(0.5, 2.0)  # Simulate varying time required for each file
            self.log_text.insert("end", f"Transmitting: {file}...\n")
            self.log_text.see("end")

            elapsed_time = 0
            while elapsed_time < work_duration:
                # Gradually update progress for the current file
                step_duration = random.uniform(0.05, 0.2)
                time.sleep(step_duration)
                elapsed_time += step_duration
                partial_progress = min(elapsed_time / work_duration, 1.0) * (1 / total_files)
                current_progress = ((idx - 1) / total_files) + partial_progress
                self.progress_bar.set(current_progress)
                self.update_idletasks()

            # Update log after each file transmission
            self.log_text.insert("end", f"OK... Transmitted: {file}\n")
            self.log_text.see("end")

if __name__ == "__main__":
    app = ProgressBarExample()
    app.mainloop()
