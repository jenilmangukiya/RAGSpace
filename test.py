from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://postgres.ujikpxcpetpwlvwnkdrd:Jenil2002Jenil@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"
)

with engine.connect() as conn:
    print("Connected!")
