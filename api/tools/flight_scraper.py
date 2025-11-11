from dotenv import load_dotenv
import os

load_dotenv()

print("KIWI_BASE_URL:", os.getenv("KIWI_BASE_URL"))
print("KIWI_HOST:", os.getenv("KIWI_HOST"))
print("KIWI_KEY:", os.getenv("KIWI_KEY")[:5] + "*****") 