import subprocess

# Step 1: Clean the build (make clean)
clean_command = 'make clean'
subprocess.run(clean_command, shell=True, check=True)

# Step 2: Build Whisper ASR with WHISPER_COREML=1 (WHISPER_COREML=1 make -j)
build_command = 'WHISPER_COREML=1 make -j'
subprocess.run(build_command, shell=True, check=True)

# Step 3: Run Whisper ASR (./main -m models/ggml-base.en.bin -f samples/jfk.wav)
asr_command = './main -m models/ggml-base.en.bin -f samples/jfk.wav'
subprocess.run(asr_command, shell=True, check=True)

import subprocess
import multiprocessing

def run_command(command):
    subprocess.run(command, shell=True)

if __name__ == "__main__":
    # Define the list of commands you want to run concurrently
    commands = [
        "command_1",
        "command_2",
        # Add the rest of your commands here
    ]

    # Create a pool of worker processes
    pool = multiprocessing.Pool(processes=12)  # Change the number of processes as needed

    # Run the commands in parallel
    pool.map(run_command, commands)

    # Close the pool and wait for all processes to complete
    pool.close()
    pool.join()
