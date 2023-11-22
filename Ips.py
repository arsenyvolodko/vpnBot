class Ips:

    IPV4_MASK = '/32'
    IPV6_MASK = '/128'

    def __init__(self, ipv4: str = None):
        self.__ipv4 = ipv4 if '/' not in ipv4 else ipv4[:ipv4.rfind('/')]
        self.__ipv6 = self.__ipv4_to_ipv6(self.__ipv4)

    def __repr__(self):
        return f'ipv4: {self.__ipv4}, ipv6: {self.__ipv6}'

    @staticmethod
    def __ipv4_to_ipv6(ipv4: str):
        val = int(ipv4[ipv4.rfind('.') + 1:])
        return f'fd42:42:42::{val}'

    def get_ipv4(self, mask=False):
        return self.__ipv4 if not mask else self.__ipv4 + self.IPV4_MASK

    def get_ipv6(self, mask=False):
        return self.__ipv6 if not mask else self.__ipv6 + self.IPV6_MASK
