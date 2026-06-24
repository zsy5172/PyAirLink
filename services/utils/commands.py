class ATCommands:
    @staticmethod
    def _send(command):
        """Private method to format command with carriage return and newline, then encode."""
        return (command + "\r\n").encode()

    @staticmethod
    def base(command):
        """ . """
        return ATCommands._send(command)

    @staticmethod
    def at():
        """ AT test command. """
        return ATCommands._send("AT")

    @staticmethod
    def cpin(pin=None):
        """ Check PIN status or enter a PIN. """
        command = "AT+CPIN"
        if pin is not None:
            command += f"={pin}"
        elif pin is None:
            command += "?"
        return ATCommands._send(command)

    @staticmethod
    def cmgf(mode=0):
        """ Set SMS message format. Mode 0 for PDU mode, 1 for text mode. """
        return ATCommands._send(f"AT+CMGF={mode}")

    @staticmethod
    def cscs(charset='UCS2'):
        """ Set TE character set, e.g., "UCS2" or "GSM". """
        return ATCommands._send(f'AT+CSCS="{charset}"')

    @staticmethod
    def cnmi(mode=2, mt=0, bm=0, ds=0, bfr=0):
        """
        设置短信新消息提示方式的AT指令（AT+CNMI）。
        根据GSM 07.05/3GPP TS 27.005协议规范，不同参数控制TA与TE之间的新消息上报和缓冲策略。

        参数说明：
        mode:
            定义TA向TE传送非请求结果码（URC）的方式（如新短信提示等）。
            取值范围：0-3
            0：TA缓冲非请求结果码，若缓冲满则丢弃最旧的提示，用新收到的代替。
            1：若TA-TE链路被占用（例如数据模式下），则丢弃非请求结果码提示，且拒收新短信的非请求提示。否则直接上报给TE。
            2：若TA-TE链路被占用（如数据模式），则在TA中缓冲结果码，链路释放后统一上报给TE。否则直接上报给TE。
            3：在数据模式下通过特定连接技术同时传输结果码和数据给TE。

        mt:
            定义新SMS-DELIVER消息的上报方式。
            取值范围：0-3
            0：不对新到的SMS-DELIVER进行直接上报，只储存在模块存储区。TE需要查询才可获知。
            1：当接收短信后，以 +CMTI: <mem>,<index> 的形式上报消息位置（需TE随后使用AT+CMGR读取）。
            2：新短信（类别0和消息等待指示组中指定为存储的短信）直接以 +CMT 或 +CMTI 的形式上报给TE（不缓存）。
            3：在2的基础上，类别3短信直接通过 +CMT 上报给TE，其他短信仍类似1的处理方式。

        bm:
            定义小区广播短信（CBM）的上报方式。
            取值范围：0、2（特定实现可能有差异）
            0：不向TE上报CBM接收指示。
            2：收到CBM后直接通过 +CBM: ... 指令上报给TE。

        ds:
            定义短信状态报告（STATUS-REPORT）的上报方式。
            取值范围：0-1
            0：不上报状态报告指示到TE。
            1：当收到状态报告时，以 +CDS 的形式直接上报给TE。

        bfr:
            当mode为1～3时，定义是否处理TA内部已经缓冲的结果码。
            取值范围：0-1
            0：在执行本设置前已存在于TA缓冲区的结果码，会在本设置生效后发送给TE。
            1：清空TA中相关的非请求结果码缓冲，不再将其发送给TE。

        当执行AT+CNMI指令后，模块会根据设置的策略决定是否立即上报新消息、缓冲结果码、或等待TE查询时才提供消息内容。
        """
        return ATCommands._send(f"AT+CNMI={mode},{mt},{bm},{ds},{bfr}")

    @staticmethod
    def cmgl(stat=0):
        """
        读取短信
        0已接收的未读消息
        1 已接收的已读消息
        2 已存储的未发送短信
        3 已存储的已发送短信
        4 所有短信
        且返回如下：
            +CMGL:<index>,<stat>,[<alpha>],<length><CR><LF>< pdu><CR><LF>+CMGL:<index>,<stat>,[<alpha>],<length><CR><LF><pdu>[...]]
            OK
        :param stat:
        :return:
        """
        return ATCommands._send(f"AT+CMGL={stat}")

    @staticmethod
    def cmgd(index=1, delflag=3):
        """
        删除短信，且返回如下：
            +CMGL:<index>,<stat>,[<alpha>],<length><CR><LF>< pdu><CR><LF>+CMGL:<index>,<stat>,[<alpha>],<length><CR><LF><pdu>[...]]
            OK
        :param index: 这个设置命令是删除<mem>1中索引为index的短信
        :param delflag: 这个设置命令是删除所有状态为<delflag>的短信。当<delflag>不等于0时，<index>参数被忽略
                        0 删除指定位置号码为<index>的短消息
                        1 删除优选存储器其中所有已读的短消息，保留未读短消息和已存储的MO短消息（无论是否发送）MO:Mobile Originated
                        2 删除优选存储器中所有已读的消息和已发送的MO短消息，保留未读的以及未发送的已存储MO短消息
                        3 删除优选存储器中所有已读的短消息，已发送和未发送的已存储MO短消息，保留未读的短消息
                        4 删除优选存储器中包括未读在内所有的短消息
        :return:
        """
        return ATCommands._send(f"AT+CMGD={index},{delflag}")

    @staticmethod
    def cgatt(attach=None):
        """ GPRS Attach or Detach. Query or set the attachment status. """
        command = "AT+CGATT"
        if attach is not None:
            command += f"={attach}"
        else:
            command += "?"
        return ATCommands._send(command)

    @staticmethod
    def cmgs(to):
        """ Prepare for sending a message. The command must be followed by the PDU and Ctrl-Z. """
        return ATCommands._send(f"AT+CMGS={to}")

    @staticmethod
    def cpms(mem='SM'):
        """ Set up a short message storage area; "SM" stands for SIM card. """
        return ATCommands._send(f'AT+CPMS="{mem}","{mem}","{mem}"')

    @staticmethod
    def reset():
        """ restart module """
        return ATCommands._send(f"AT+RESET")

at_commands = ATCommands()

if __name__ == "__main__":
    # Example Usage:
    print(ATCommands.at())
    print(ATCommands.cpin())
    print(ATCommands.cmgf(0))
    print(ATCommands.cscs("UCS2"))
    print(ATCommands.cnmi(2, 2, 0, 0, 0))
    print(ATCommands.cgatt())
    print(ATCommands.cmgs("+1234567890"))
    print(ATCommands.cmgl(stat=0))
    print(ATCommands.cmgd(index=1))
