class FakeRequest:

    class FakeUser:
        pass

    def __init__(self):
        self.user = self.FakeUser()
        self.user.username = 'emily.lulala@gmail.com'


if __name__ == '__main__':
    request = FakeRequest()