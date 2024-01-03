import os
import logging

class Configuration:

    def __init__(
            self,
            base_url: str = "http://localhost:8080",
            debug: bool = False,
            server_api_url: str = None,
    ):
        if server_api_url != None:
            self.host = server_api_url
        else:
            self.host = base_url + '/api'

        self.temp_folder_path = None

        # Debug switch
        self.debug = debug
        
        # Log format
        self.logger_format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'

        # SSL/TLS verification
        # Set this to false to skip verifying SSL certificate when calling API
        # from https server.
        self.verify_ssl = True
        
        # Set this to customize the certificate file to verify the peer.
        self.ssl_ca_cert = None
        
        # client certificate file
        self.cert_file = None
        
        # Set this to True/False to enable/disable SSL hostname verification.
        self.assert_hostname = None

        # Proxy URL
        self.proxy = None
        
        # Safe chars for path_param
        self.safe_chars_for_path_param = ''

        # Provide an alterative to requests.Session() for HTTP connection.
        self.http_connection = None

    @property
    def debug(self):
        """Debug status

        :param value: The debug status, True or False.
        :type: bool
        """
        return self.__debug

    @debug.setter
    def debug(self, value):
        """Debug status

        :param value: The debug status, True or False.
        :type: bool
        """
        self.__debug = value
        if self.__debug:
            self.__log_level = logging.DEBUG
        else:
            self.__log_level = logging.INFO

    @property
    def logger_format(self):
        """The logger format.

        The logger_formatter will be updated when sets logger_format.

        :param value: The format string.
        :type: str
        """
        return self.__logger_format

    @logger_format.setter
    def logger_format(self, value):
        """The logger format.

        The logger_formatter will be updated when sets logger_format.

        :param value: The format string.
        :type: str
        """
        self.__logger_format = value

    def apply_logging_config(self):
        logging.basicConfig(
            format=self.logger_format,
            level=self.__log_level
        )

    @staticmethod
    def get_logging_formatted_name(name):
        return f'[{os.getpid()}] {name}'

