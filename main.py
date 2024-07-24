import os
import json
import subprocess
import time

CONFIG_DIR = 'configs'  # Carpeta donde se encuentran los archivos JSON

def load_config_files(config_dir):
    """Carga todos los archivos de configuración JSON desde una carpeta."""
    config_files = [f for f in os.listdir(config_dir) if f.endswith('.json')]
    return [os.path.join(config_dir, f) for f in config_files]

def parse_config(file_path):
    """Parsea un archivo de configuración JSON."""
    with open(file_path, 'r') as file:
        return json.load(file)

def start_stream(script_path):
    """Inicia un script y retorna el proceso."""
    return subprocess.Popen(['python', script_path])

def main():
    config_files = load_config_files(CONFIG_DIR)
    processes = []
    
    for config_file in config_files:
        config = parse_config(config_file)
        for stream in config['streams']:
            script_path = stream['script_path']
            process = start_stream(script_path)
            processes.append((stream['name'], process))
            print(f"Started {stream['name']} with PID {process.pid}")
    
    # Monitorear los procesos
    try:
        while True:
            for name, process in processes:
                if process.poll() is not None:  # El proceso ha terminado
                    print(f"Process {name} (PID {process.pid}) ended.")
                    # Reiniciar el proceso si es necesario
                    script_path = [stream['script_path'] for stream in parse_config(config_file)['streams'] if stream['name'] == name][0]
                    process = start_stream(script_path)
                    processes.append((name, process))
                    print(f"Restarted {name} with PID {process.pid}")
            time.sleep(5)  # Esperar antes de volver a comprobar
    except KeyboardInterrupt:
        print("Shutting down...")
        for name, process in processes:
            process.terminate()
            print(f"Terminated {name} (PID {process.pid})")

if __name__ == "__main__":
    main()
