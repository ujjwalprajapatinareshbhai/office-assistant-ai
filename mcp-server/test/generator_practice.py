import time


def office_assistant():

    yield "Searching weather..."
    time.sleep(2)

    yield "Getting forecast..."
    time.sleep(2)

    yield "Preparing report..."
    time.sleep(2)

    yield "Sending email..."
    time.sleep(2)

    yield "Done!"

for message in office_assistant():
    print(message)