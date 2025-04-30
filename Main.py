import requests
import hashlib
import platform
import uuid
import sys
import os
from datetime import datetime
from cryptography.fernet import Fernet
import webbrowser
from dotenv import load_dotenv, set_key

load_dotenv()

class KeyAuth:
    def __init__(self, name, ownerid, secret, version):
        self.name = name
        self.ownerid = ownerid
        self.secret = secret
        self.version = version
        self.sessionid = ""
        self.initialized = False

        self.encryption_key = os.getenv("ENCRYPTION_KEY")
        if not self.encryption_key:
            self.encryption_key = Fernet.generate_key().decode()
            env_path = os.path.join(os.getcwd(), '.env')
            set_key(env_path, "ENCRYPTION_KEY", self.encryption_key)
            print(f"[INFO] Generated new ENCRYPTION_KEY and updated .env file automatically.")

        self.fernet = Fernet(self.encryption_key.encode())

    def init(self):
        if self.initialized:
            return True

        data = {
            "type": "init",
            "name": self.name,
            "ownerid": self.ownerid,
            "ver": self.version
        }

        try:
            response = self.__request(data, first_call=True)
            if response["success"]:
                self.sessionid = response["sessionid"]
                self.initialized = True
                return True
            else:
                print(f"[Error] Initialization failed: {response.get('message', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"[Error] Initialization error: {str(e)}")
            return False

    def login(self, username, password):
        if not self.initialized and not self.init():
            return False, "System not initialized"

        hwid = self.__get_hwid()

        data = {
            "type": "login",
            "username": username,
            "pass": password,
            "hwid": hwid,
            "sessionid": self.sessionid,
            "name": self.name,
            "ownerid": self.ownerid
        }

        try:
            response = self.__request(data)
            if response.get("success"):
                print(f"\n[Success] Login successful! Welcome {username}")
                print(f"IP Address: {self.get_ip_address()}")
                print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                return True, response.get("message", "Login successful")
            else:
                return False, response.get("message", "Unknown error")
        except Exception as e:
            return False, f"Login error: {str(e)}"

    def register_with_license(self, license_key):
        if not self.initialized and not self.init():
            return False, "System not initialized"

        hwid = self.__get_hwid()

        data = {
            "type": "license",
            "key": license_key,
            "hwid": hwid,
            "sessionid": self.sessionid,
            "name": self.name,
            "ownerid": self.ownerid
        }

        try:
            response = self.__request(data)

            if not response.get("success"):
                return False, f"License Invalid: {response.get('message', 'Unknown error')}"

            print("\n[Success] License validated! Now create your new account.")

            # Now ask for username and password
            username = input("Create Username: ").strip()
            password = input("Create Password: ").strip()

            if not username or not password:
                return False, "Username and password cannot be empty."

            # Encrypt password
            encrypted_password = self.encrypt_password(password)

            register_data = {
                "type": "register",
                "username": username,
                "pass": encrypted_password,
                "hwid": hwid,
                "sessionid": self.sessionid,
                "name": self.name,
                "ownerid": self.ownerid
            }

            reg_response = self.__request(register_data)

            if reg_response.get("success"):
                return True, "Registration completed successfully!"
            else:
                return False, reg_response.get("message", "Registration failed.")

        except Exception as e:
            return False, f"Registration error: {str(e)}"

    def check_license_validity(self, license_key):
        if not self.initialized and not self.init():
            return False, "System not initialized"

        hwid = self.__get_hwid()

        data = {
            "type": "license",
            "key": license_key,
            "hwid": hwid,
            "sessionid": self.sessionid,
            "name": self.name,
            "ownerid": self.ownerid
        }

        try:
            response = self.__request(data)
            if response.get("success"):
                return True, "License is valid!"
            else:
                return False, response.get("message", "License is invalid.")
        except Exception as e:
            return False, f"License check error: {str(e)}"

    def __request(self, data, first_call=False):
        if not first_call:
            data["enckey"] = self.__get_encryption_key()

        try:
            response = requests.post("https://hyperb57p-qipp.tryxcloud.cc/api/1.2/", data=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        except ValueError:
            raise Exception("Invalid API response (Not JSON)")

    def encrypt_password(self, password):
        try:
            return self.fernet.encrypt(password.encode()).decode()
        except Exception as e:
            raise Exception(f"Password encryption failed: {str(e)}")

    def __get_encryption_key(self):
        if not self.sessionid:
            raise Exception("Session ID not available.")
        return hashlib.sha256((self.secret + self.sessionid + self.name + self.ownerid).encode()).hexdigest()

    def __get_hwid(self):
        hwid = str(platform.processor()) + str(uuid.getnode())
        return hashlib.sha256(hwid.encode()).hexdigest()

    def get_ip_address(self):
        try:
            response = requests.get("https://api.ipify.org?format=json", timeout=5)
            return response.json().get("ip", "Unavailable")
        except requests.exceptions.RequestException:
            return "Unavailable"

def main():
    auth = KeyAuth(
     name = "12", # App name - VaultCord.com FREE Discord backup bot for members & your entire server saved from terms and nukes!
    ownerid = "V1LLAOf0D7", # Account ID
    version = "1.0", 
    secret="103560211cc62b16340562ff803e8442b55b822ba0bb65cbeb5e632718647cbf",

    )

    print("=== Welcome to the System ===")
    while True:
        print("\nOptions:")
        print("(1) Register with License Key")
        print("(2) Login with Username & Password")
        print("(3) Check License Validity")
        print("(q) Quit")

        action = input("Select an option: ").strip().lower()

        if action == "q":
            print("Goodbye!")
            sys.exit(0)

        elif action == "1":
            webbrowser.open("https://www.pnel-check.wuaze.com/")

        elif action == "2":
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            if not username or not password:
                print("[Error] Username and password cannot be empty.")
                continue
            success, message = auth.login(username, password)
            if success:
                print("[Info] You are logged in.")
            else:
                print("\n[Error]", message)

        elif action == "3":
            license_key = input("Enter your License Key to validate: ").strip()
            if not license_key:
                print("[Error] License key cannot be empty.")
                continue
            success, message = auth.check_license_validity(license_key)
            if success:
                print("\n[Success]", message)
            else:
                print("\n[Error]", message)

        else:
            print("[Error] Invalid option selected.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected Error: {str(e)}")
        sys.exit(1)
