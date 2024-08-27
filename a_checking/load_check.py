import requests
import time

def load_test(url, num_requests):
    """
    Performs load testing on the specified URL by sending multiple requests concurrently.

    Args:
        url: The URL to test.
        num_requests: The number of requests to send.
    """

    start_time = time.time()

    for _ in range(num_requests):
        response = requests.get(url, stream=True)
        response.close()

    end_time = time.time()

    elapsed_time = end_time - start_time
    requests_per_second = num_requests / elapsed_time

    print(f"Sent {num_requests} requests in {elapsed_time:.2f} seconds.")
    print(f"Average requests per second: {requests_per_second:.2f}")
import threading
if __name__ == "__main__":
    url = "http://172.16.7.99/lvfile/api/developer/file/1bd7aafd-781e-489d-8f56-0a4cc9fb54d3/24-08%20quy%E1%BA%BFt%20to%C3%A1n%20chi%20ph%C3%AD%20s%E1%BB%ADa%20xe%20t%E1%BB%AB%20ng%C3%A0y%2014.07-24.08.pdf"  # Replace with your URL
    num_requests = 1000  # Adjust the number of requests as needed
    num_threads = 200  # Adjust the number of threads as needed
    while True:
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=load_test, args=(url, num_requests))
            threads.append(thread)
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()
