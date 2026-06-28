from pathlib import Path

from services.share_service import (
    ShareService,
)


def main():

    sample = (
        Path(__file__).parent
        / "sample.pdf"
    )

    if not sample.exists():

        print(
            "sample.pdf not found."
        )

        return

    result = (
        ShareService().share(
            str(sample)
        )
    )

    print()

    print("=" * 60)

    print(
        "FILE SHARED SUCCESSFULLY"
    )

    print("=" * 60)

    for key, value in result.items():

        print(
            f"{key}: {value}"
        )


if __name__ == "__main__":

    main()