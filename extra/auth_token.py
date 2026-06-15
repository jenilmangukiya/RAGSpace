from supabase import create_client

url = ""
key = ""

supabase = create_client(url, key)

response = supabase.auth.sign_in_with_password({"email": "", "password": ""})

session = response.session
access_token = session.access_token

print("JWT Token:", access_token)
