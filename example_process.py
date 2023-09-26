import multiprocessing
import threading

def child_thread_function(index):
    print(f"thread {index} created")


# Create a list of child threads.
child_threads = []
for i in range(10):
  child_thread = threading.Thread(target=child_thread_function, args=(i,))
  child_threads.append(child_thread)

# Create a process.
p = multiprocessing.Process(target=child_thread_function, args=(i,))

# Start the process.
p.start()

# Join all of the child threads.
for child_thread in child_threads:
  child_thread.join()

# Wait for the process to finish.
p.join()