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


## need to read the model from /root/.choline/choline.yaml under the 'model' key/val
        
######## then we will make sure it's been pulled by checking /root/.ollama/models/manifests/registry.ollama.ai/library/{modelName}

###### if it hasnt been pulled, u need to pull it 
        
# /usr/bin/ollama pull mistral > /var/log/ollama_pull.log 2>&1 &

# # Wait for the pull to complete successfully
# echo "Waiting for ollama to pull the model..."
# while ! grep -q "success" /var/log/ollama_pull.log; do
#   sleep 10 # Check every 10 seconds
# done

# echo "Model pull completed successfully."



# def generate_response(prompt):
#     curl_command = f"""curl -s http://localhost:11434/api/generate -d '{{"model": "mistral", "prompt":"{prompt}"}}'"""
    
#     process = subprocess.Popen(curl_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#     full_response = ""
        
#     while True:
#         output_line = process.stdout.readline()
#         if not output_line and process.poll() is not None:
#             break
#         if output_line:
#             try:
#                 response_data = json.loads(output_line.strip())
#                 full_response += response_data.get("response", "")
#             except json.JSONDecodeError:
#                 return "Invalid response format", 500

#     return full_response


import subprocess
import yaml
import os
import time
import json

def read_model_from_config(config_path='/root/.choline/choline.yaml'):
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            return config.get('model')
    except Exception as e:
        print(f"Failed to read config: {str(e)}")
        return None

def check_model_pulled(model_name):
    model_manifest_path = f"/root/.ollama/models/manifests/registry.ollama.ai/library/{model_name}"
    return os.path.exists(model_manifest_path)

def pull_model(model_name):
    pull_command = f"/usr/bin/ollama pull {model_name} > /var/log/ollama_pull.log 2>&1 &"
    subprocess.run(pull_command, shell=True)

def wait_for_model_pull():
    print("Waiting for ollama to pull the model...")
    while True:
        with open('/var/log/ollama_pull.log', 'r') as log_file:
            if "success" in log_file.read():
                print("Model pull completed successfully.")
                break
        time.sleep(10)  # Check every 10 seconds

def generate_response(prompt, config_path='/root/.choline/choline.yaml'):
    model_name = read_model_from_config(config_path)
    if model_name is None:
        print("Model name not found in config.")
        return "Model name not found in config."

    if not check_model_pulled(model_name):
        # pull_model(model_name)
        # wait_for_model_pull() 
        return "Model does not exist on this instance"

    curl_command = f"""curl -s http://localhost:11434/api/generate -d '{{"model": "{model_name}", "prompt":"{prompt}"}}'"""
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