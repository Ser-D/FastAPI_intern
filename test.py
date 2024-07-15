from jose import jwt, JWTError

def decode_token(token: str) -> dict:
    try:
        payload = jwt.get_unverified_claims(token)
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")

# Приклад використання:
token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkUxcFpFMGNvZE1JaDR1QlpWZ3YtYyJ9.eyJlbWFpbCI6InNlcl8wMDFAbWV0YS51YSIsImlzcyI6Imh0dHBzOi8vZGV2LWh4N3ljOHdsMzZvZHZiaGwudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDY2OGYwMGQ0NjcxYzQwN2U4YTkzZGRlOCIsImF1ZCI6WyJodHRwczovL215MS5jb20iLCJodHRwczovL2Rldi1oeDd5Yzh3bDM2b2R2YmhsLnVzLmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE3MjA3NzYyMjIsImV4cCI6MTcyMDg2MjYyMiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsImF6cCI6Ilc1azFJWjJDbG0wUWNTbHZodlU1eFBwS0Y5OUlkMlBnIn0.bgIfUU_OIw9m0SDbiBR6LRKtANN8KSweEB0oBoR6EZXL0J29u89TgHXKe1A5tlIJ14E49-iClMm_810W0Ab0NGtwse9Pb1ALWJFRS3S1geqQEVZGXCNymLaLkFBswMl7ONdQMRJ1WYupTr5EX3zjVWryrSwJnTW3UlF7SOkH138uy4iDA5nHCI6RFiPkFnoOulGlDCGCYVEYEy9XTnebS7MwDD4RGnVbz2C5VJIKNm9Ro13Wh_YCs3x1c-_EARvX0qVn5RjA363XoIZ1v5aMgABGgbT2pMIrSkv4A1trw3Zb3-Te9M8coCwKaPL9jzdTcspXFc3guBVQQIzD58LoxA"
try:
    decoded_payload = decode_token(token)
    print("Payload:", decoded_payload)
except ValueError as e:
    print(e)