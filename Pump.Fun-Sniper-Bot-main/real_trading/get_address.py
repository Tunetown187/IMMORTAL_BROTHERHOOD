from solders.keypair import Keypair

private_key = "2FFhe61Db5oHyYQ5yQ6QN5mnsUMpSwJ8kNQPvrC23L18o2uNkCR4V3y7QzWkTpWvHX6YJqB7BNyz6kNE1EUDuBjW"
keypair = Keypair.from_base58_string(private_key)
print(f"Your wallet address: {keypair.pubkey()}")
