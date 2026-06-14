from services.peer_registration_service import RegistrationService


def main():

    response = (
        RegistrationService
        .register()
    )

    print(response)


if __name__ == "__main__":
    main()