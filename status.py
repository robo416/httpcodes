import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Input and output files
input_file = "urls.txt"  # File containing URLs (one per line)
output_2xx = "2xx.txt"  # File to save URLs with 2xx status codes
output_3xx = "3xx.txt"  # File to save URLs with 3xx status codes

# Function to check HTTP status
def check_status(url):
    try:
        # Ensure the URL starts with "http://" or "https://"
        if not url.startswith(("http://", "https://")):
            url = "https://" + url  # Default to HTTPS if no scheme is provided

        # Send a GET request with a timeout and disable redirects
        response = requests.get(url, timeout=10, allow_redirects=False)

        # Check for 2xx and 3xx status codes
        if 200 <= response.status_code < 300:  # 2xx range
            return url, response.status_code, "2xx"
        elif 300 <= response.status_code < 400:  # 3xx range
            return url, response.status_code, "3xx"
    except requests.RequestException as e:
        # Print errors for debugging
        print(f"Error checking {url}: {e}")
    return None

# Read URLs from the input file
with open(input_file, "r") as file:
    urls = file.read().splitlines()

# Open output files in append mode
with open(output_2xx, "w") as file_2xx, open(output_3xx, "w") as file_3xx:
    # Process URLs in parallel
    with ThreadPoolExecutor(max_workers=100) as executor:  # Increase max_workers for more concurrency
        futures = {executor.submit(check_status, url): url for url in urls}

        # Write results to files as they are completed
        for future in as_completed(futures):
            result = future.result()
            if result:  # Only write URLs with valid status codes
                url, status_code, category = result
                if category == "2xx":
                    file_2xx.write(f"{url} {status_code}\n")
                    file_2xx.flush()  # Ensure the result is written immediately
                elif category == "3xx":
                    file_3xx.write(f"{url} {status_code}\n")
                    file_3xx.flush()  # Ensure the result is written immediately

print(f"2xx results saved to {output_2xx}")
print(f"3xx results saved to {output_3xx}")