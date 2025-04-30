async def login_and_report(phone, target_username, reason_key, message_urls, report_count):
    """Handles login and reporting for a single account."""
    session_file = f"sessions/{phone.replace('+', '')}.session"

    if os.path.exists(session_file):
        try:
            with open(session_file, "rb") as f:
                if not f.read():
                    print(f"✗ Corrupted session for {phone}, deleting...")
                    os.remove(session_file)
        except Exception as e:
            print(f"✗ Error reading session for {phone}: {e}")
            os.remove(session_file)

    try:
        async with TelegramClient(session_file, API_ID, API_HASH) as client:
            await client.start(phone)
            print(f"✓ Logged in with {phone}")
            await report_messages(client, target_username, reason_key, message_urls, report_count)
    except sqlite3.OperationalError:
        print(f"✗ Session database error for {phone}. Deleting and retrying...")
        os.remove(session_file)
        return await login_and_report(phone, target_username, reason_key, message_urls, report_count)
    except PhoneNumberBannedError:
        print(f"✗ Account {phone} is banned! Skipping...")
    except SessionPasswordNeededError:
        print(f"✗ Account {phone} requires a password! Enter it manually.")

async def main():
    """Main function to initiate mass reporting."""
    print(BANNER)

    if not os.path.exists(ACCOUNTS_FILE):
        print(f"✗ Error: {ACCOUNTS_FILE} not found!")
        return

    with open(ACCOUNTS_FILE, "r") as f:
        phone_numbers = [line.strip() for line in f if line.strip()]

    if not phone_numbers:
        print("✗ No accounts found in accounts.txt!")
        return

    target_username = input("Enter Username or Group (@username): ").strip()

    print("\nChoose Report Reason:")
    for key, (reason_text, _) in REPORT_REASONS.items():
        print(f"   {key}. {reason_text}")

    reason_key = input("\nEnter Report Reason (1-10): ").strip()
    while reason_key not in REPORT_REASONS:
        print("✗ Invalid selection! Enter a number between 1-10.")
        reason_key = input("Enter Report Reason (1-10): ").strip()

    report_count = int(input("How many messages to report?: "))

    if not os.path.exists(SELECT_MSG_FILE):
        print(f"✗ Error: {SELECT_MSG_FILE} not found!")
        return

    with open(SELECT_MSG_FILE, "r") as f:
        message_urls = [line.strip() for line in f if line.strip()]

    if not message_urls:
        print("✗ No messages found in select_msg.csv!")
        return

    os.makedirs("sessions", exist_ok=True)

    for phone in phone_numbers:
        print(f"\n♛ Logging in with account: {phone}")
        await login_and_report(phone, target_username, reason_key, message_urls, report_count)

asyncio.run(main())
