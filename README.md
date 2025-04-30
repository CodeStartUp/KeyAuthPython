Project Authentication Setup
🔐 KeyAuth Integration
This project uses KeyAuth for secure authentication. Follow these steps to configure it properly.

🚀 Quick Setup
Replace API Endpoint:

python
response = requests.post(
    "https://your-custom-url.keyauth.com/api/1.2/",  # Replace with your KeyAuth URL
    data=data,
    timeout=10
)
Authentication Setup:

python
auth = KeyAuth(
    name="your_app_name",       # From KeyAuth dashboard
    ownerid="your_owner_id",    # From KeyAuth account
    version="1.0",             # Your app version
    secret="your_secret_key"   # From KeyAuth app settings
)
⚠️ Security Notice
