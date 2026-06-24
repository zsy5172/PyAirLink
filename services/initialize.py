from io import StringIO
import time
import logging
from zoneinfo import ZoneInfo

from services.notification import serverchan, send_email, bark, wecom
from services.utils.config_parser import config
from services.utils.serial_manager import SerialManager
from .utils.sms import parse_pdu, encode_pdu
from .utils.commands import at_commands

logger = logging.getLogger("PyAirLink")


def _at_ok(response):
    return bool(response) and "OK" in response and "ERROR" not in response


def _configure_sms_storage(serial_manager):
    for mem in ("SM", "ME"):
        response = serial_manager.send_at_command(at_commands.cpms(mem=mem), keywords="OK")
        if _at_ok(response):
            logger.info("SMS storage is set to %s", mem)
            return True
        logger.warning("Unable to set SMS storage to %s, response: %s", mem, response)
    return False


def web_send_at_command(command, keywords=None, timeout=3):
    with SerialManager() as serial_manager:
        response = serial_manager.send_at_command(command, keywords=keywords, timeout=timeout)
        return response


def initialize_module():
    """
    初始化模块
    """
    logger.info("Initializing modules...")

    # 发送基本AT指令
    with SerialManager() as serial_manager:
        response = serial_manager.send_at_command(at_commands.at(), keywords="OK")
        if not _at_ok(response):
            logger.error("Unable to communicate with module")
            return False

        response = serial_manager.send_at_command(at_commands.cpin(), keywords="OK")
        if not _at_ok(response) or "READY" not in response:
            logger.error("SIM card not detected, please check and restart the module")
            return False
        logger.info("SIM card ready")

        response = serial_manager.send_at_command(at_commands.cmgf(), keywords="OK")
        if not _at_ok(response):
            logger.error("Unable to set SMS format to PDU")
            return False
        logger.info("SMS format is set to PDU")

        response = serial_manager.send_at_command(at_commands.cscs(), keywords="OK")
        if not _at_ok(response):
            logger.error("Unable to set character set to UCS2")
            return False
        logger.info("Character set is set to UCS2")

        if not _configure_sms_storage(serial_manager):
            logger.error("Unable to configure new SMS buffer")
            return False
        logger.info("New SMS buffer configuration completed")

        response = serial_manager.send_at_command(at_commands.cnmi(), keywords="OK")
        if not _at_ok(response):
            logger.error("Unable to configure new SMS notifications")
            return False
        logger.info("New SMS notification configuration completed")

        # 检查 GPRS 附着状态
        while True:
            response = serial_manager.send_at_command(at_commands.cgatt(), keywords="+CGATT: 1")
            if response:
                logger.info("GPRS Attached")
                break
            else:
                logger.warning("GPRS not attached, retrying in 5 seconds...")
                time.sleep(5)

        response = serial_manager.send_at_command(at_commands.cmgd(index=1, delflag=2), keywords=['OK'])
        if not _at_ok(response):
            logger.error("Unable to delete read messages, and unable to receive new messages if the storage area is full")
        logger.info("All read messages have been deleted")

    logger.info("Module initialization completed")
    return True


def web_restart():
    with SerialManager() as serial_manager:
        resp = serial_manager.send_at_command(at_commands.reset())
        if not resp:
            logger.warning("Module restart failed")
        else:
            logger.info("Module restart successful")
    time.sleep(3)
    return initialize_module()


def handle_sms(phone_number, sms_content, receive_time, tz="Asia/Shanghai"):
    """
    处理接收到的短信
    """
    logger.info(f"Received SMS from {phone_number} at {receive_time}, content: {sms_content}")
    channels = {'serverchan': serverchan, 'mail': send_email, 'bark': bark, 'wecom': wecom}
    use_channels = config.notification()
    if use_channels:
        title = f'new sms from {phone_number}'
        content = f'{sms_content},\nreceive time: {receive_time.astimezone(ZoneInfo(tz))}'
        for channel in use_channels:
            func = channels[channel]
            try:
                func(title, content)
            except Exception as e:
                logger.error(f'SMS push error, channel type: {channel}, error: {e}')
    return True


def send_sms(to, text):
    """
    使用AT指令在PDU模式下发送SMS。
    ser是已打开的pyserial串口对象。
    to为目标号码字符串（如"+8613800138000"），text为短信内容（UTF-8字符串）。
    """
    logging_tag = "send_sms"
    pdu, length = encode_pdu(to, text)
    if not pdu or not length:
        logger.error("%s: SMS encoding failed", logging_tag)
        return False

    # 设置CMGF=0进入PDU模式（如果之前没设置过）
    with SerialManager() as serial_manager:
        resp = serial_manager.send_at_command(at_commands.cmgf())
        if not resp:
            logger.error("%s: Unable to enter PDU mode", logging_tag)
            return False

        # 发送AT+CMGS指令
        resp = serial_manager.send_at_command(at_commands.cmgs(length), keywords='>', timeout=3)
        if not resp:
            logger.error("%s: Receive SMS message sending prompt '>' timeout", logging_tag)
            return False

        # 发送PDU数据和Ctrl+Z结束符(0x1A)
        resp = serial_manager.send_at_command(pdu.encode('utf-8') + b'\x1A', keywords='+CMGS:', timeout=5)
        logger.debug("%s: PDU data has been sent, waiting for URC to be sent successfully", logging_tag)
        if resp:
            logger.info("%s: SMS sent successfully", logging_tag)
            return True
        else:
            logger.error("%s: No confirmation message of '+CMGS' was received, sending failed", logging_tag)
            return False


def sms_listener(stop_event):
    """
    定期查询是否有新短信的监听器
    """
    with SerialManager() as serial_manager:
        while not stop_event.is_set():
            try:
                # 发送AT+CMGL命令查询未读短信
                response = serial_manager.send_at_command(at_commands.cmgl(stat=0), keywords=['OK'])
                # logger.warning(f"本次查询短信收到回复: {response}")
                if response and '+CMGL:' in response:
                    lines = response.strip().splitlines()
                    i = 0
                    massages = []
                    while i < len(lines):
                        line = lines[i].strip()
                        if line.startswith('+CMGL:'):
                            # 当前行为短信头，下一行应为 PDU 数据
                            if i + 1 < len(lines):
                                pdu_line = lines[i + 1].strip()
                                # 解析短信通知
                                try:
                                    match = parse_pdu(StringIO(pdu_line))
                                    if isinstance(match, dict):
                                        massages.append(match)
                                    else:
                                        logger.warning(f"Incorrect parsing of PDU: {pdu_line}")
                                except Exception as e:
                                    logger.error(f"Parsing PDU: {pdu_line}\nerror: {e}\nresponse: {response}")
                                i += 2  # 跳过 PDU 数据行，继续处理下一条短信
                            else:
                                # 错误处理：+CMGL 行后没有 PDU 数据
                                logger.warning(f"At index {i}, PDU data is missing after +CMGL line")
                                i += 1
                        else:
                            i += 1
                    for massage in massages:
                        phone_number = massage.get('sender').get('number')
                        receive_time = massage.get('scts')
                        sms_content = massage.get('user_data').get('data')
                        handle_sms(phone_number, sms_content, receive_time)
                    serial_manager.send_at_command(at_commands.cmgd(), keywords=['OK'])
                # 短暂休眠，避免占用过多资源
                time.sleep(1)
            except Exception as e:
                logger.error(f"sms_listener error: {e}")
                time.sleep(1)


if __name__ == "__main__":
    pass
