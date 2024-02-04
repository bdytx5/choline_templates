import subprocess
import json
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time 


class CholineHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Check if the file is not an _out.txt file
        if not event.src_path.endswith("_out.txt") and event.src_path.endswith(".txt"):
            self.process(event.src_path)

    def process(self, file_path):
        # Extract the file ID from the file_path
        file_id = os.path.basename(file_path).replace(".txt", "")
        out_file_path = f"/root/.choline/{file_id}_out.txt"
        time.sleep(1)
        # Read the prompt from the file
        with open(file_path, 'r') as file:
            prompt = file.read()

        # Generate a response using the provided function
        response = generate_response(prompt)
        print(response)
        # Write the response to the corresponding _out.txt file
        with open(out_file_path, 'w') as file:
            file.write(response)
            file.flush()
            file.close()
            
        print(f"Processed and responded to {file_path}")

def generate_response(prompt):
    curl_command = f"""curl -s http://localhost:11434/api/generate -d '{{"model": "mistral", "prompt":"{prompt}"}}'"""
    
    process = subprocess.Popen(curl_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    full_response = ""
        
    while True:
        output_line = process.stdout.readline()
        if not output_line and process.poll() is not None:
            break
        if output_line:
            try:
                response_data = json.loads(output_line.strip())
                full_response += response_data.get("response", "")
            except json.JSONDecodeError:
                return "Invalid response format", 500

    return full_response

def start_monitoring(path='/root/.choline/'):
    event_handler = CholineHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_monitoring()