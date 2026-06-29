import logging

from api.download_api import DownloadAPI


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def main() -> None:

    print()

    print("=" * 60)
    print("MeshCDN Download Test")
    print("=" * 60)
    print()

    file_hash = input(
        "Enter file hash: "
    ).strip()

    if not file_hash:

        print(
            "\nFile hash is required."
        )

        return

    print()

    print(
        "Starting download..."
    )

    print()

    try:

        result = (
            DownloadAPI.download(
                file_hash
            )
        )

        print()

        print("=" * 60)
        print("DOWNLOAD COMPLETED")
        print("=" * 60)

        print(
            f"Status       : {result['status']}"
        )

        print(
            f"File Name    : {result['file_name']}"
        )

        print(
            f"File Hash    : {result['file_hash']}"
        )

        print(
            f"Saved To     : {result['output_path']}"
        )

        print("=" * 60)

    except Exception as exc:

        logging.exception(
            "Download failed."
        )

        print()

        print("=" * 60)
        print("DOWNLOAD FAILED")
        print("=" * 60)

        print(
            f"Reason: {exc}"
        )

        print("=" * 60)


if __name__ == "__main__":

    main()