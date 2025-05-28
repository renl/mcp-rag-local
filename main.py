import requests


def main():
    print("Hello from local-rag!")
    response = requests.get("http://example.com")
    print(f"Status code: {response.status_code}")


if __name__ == "__main__":
    main()
