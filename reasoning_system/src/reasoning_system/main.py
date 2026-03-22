from dotenv import load_dotenv

from ai import GeminiClient


def main() -> None:
    load_dotenv()

    text = (
        "User inserts card, enters PIN, and can withdraw cash. If the PIN is wrong, the user can retry. If the card is invalid, it should be handled appropriately. After cash is dispensed, print a receipt."
    )

    client = GeminiClient()
    result = client.extract_atomic_facts(text)

    print(text)

    print("\n=== Extraction Result ===")
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()