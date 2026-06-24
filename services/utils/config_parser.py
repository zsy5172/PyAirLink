from configparser import ConfigParser


class Config:
    def __init__(self, ini_path='data/config.ini', default_ini_path='config.ini.template'):
        self.config = ConfigParser()
        config_read = self.config.read(ini_path)
        if not config_read:
            print(f"Warning: '{ini_path}' not found. Using default settings.")
            self.config.read(default_ini_path)

    def sqlite_url(self):
        url = self.config.get('DATABASE', 'SQLITE')
        return f'sqlite:///data/{url}'

    def serial(self):
        port = self.config.get('SERIAL', 'PORT')
        rate = self.config.getint('SERIAL', 'BAUD_RATE')
        timeout = self.config.getint('SERIAL', 'TIMEOUT')
        return {'port': port, 'rate': rate, 'timeout': timeout}

    def server_chan(self):
        return self.config.get('SERVERCHAN', 'SENDKEY')

    def bark(self):
        url = self.config.get('BARK', 'URL', fallback='')
        key = self.config.get('BARK', 'KEY', fallback='')
        return {'url': url, 'key': key}

    def wecom(self):
        key = self.config.get('WECOM', 'KEY', fallback='')
        return {'key': key}

    def mail(self):
        smtp_server = self.config.get('MAIL', 'SMTP_SERVER')
        smtp_port = self.config.getint('MAIL', 'SMTP_PORT')
        account = self.config.get('MAIL', 'ACCOUNT')
        password = self.config.get('MAIL', 'PASSWORD')
        mail_to = self.config.get('MAIL', 'MAIL_TO')
        tls = self.config.getboolean('MAIL', 'TLS')
        return {'smtp_server': smtp_server, 'smtp_port': smtp_port, 'account': account, 'password': password, 'mail_to': mail_to, 'tls': tls}

    def notification(self):
        channels = self.config.get('NOTIFICATION', 'CHANNELS').split(',')
        return [channel.strip() for channel in channels] if channels else []

config = Config()
