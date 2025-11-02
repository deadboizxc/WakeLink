#!/usr/bin/env python3
"""
WakeLink Client v1.0
"""
import argparse
import sys
import os
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(__file__))

from config.device_manager import DeviceManager
from protocol.commands import WakeLinkCommands
from handlers.tcp_handler import TCPHandler
from handlers.cloud_client import CloudClient
from utils.helpers import format_mac_address  # Добавляем импорт


class OutputFormatter:
    COLORS = {
        'green': '\033[92m', 'yellow': '\033[93m', 'red': '\033[91m',
        'blue': '\033[94m', 'magenta': '\033[95m', 'cyan': '\033[96m',
        'bold': '\033[1m', 'end': '\033[0m'
    }

    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        return f"{cls.COLORS.get(color, '')}{text}{cls.COLORS['end']}"

    @classmethod
    def print_header(cls, text: str):
        print(f"\n{cls.COLORS['bold']}{cls.COLORS['cyan']}╔{'═' * (len(text) + 2)}╗{cls.COLORS['end']}")
        print(f"{cls.COLORS['bold']}{cls.COLORS['cyan']}║ {text} ║{cls.COLORS['end']}")
        print(f"{cls.COLORS['bold']}{cls.COLORS['cyan']}╚{'═' * (len(text) + 2)}╝{cls.COLORS['end']}")

    @classmethod
    def print_success(cls, text: str):   print(f"{cls.COLORS['green']}Success: {text}{cls.COLORS['end']}")
    @classmethod
    def print_error(cls, text: str):     print(f"{cls.COLORS['red']}Error: {text}{cls.COLORS['end']}")
    @classmethod
    def print_warning(cls, text: str):   print(f"{cls.COLORS['yellow']}Warning: {text}{cls.COLORS['end']}")
    @classmethod
    def print_info(cls, text: str):      print(f"{cls.COLORS['blue']}Info: {text}{cls.COLORS['end']}")

    @classmethod
    def print_command(cls, command: str, mode: str):
        mode_icon = "Cloud" if mode == "CLOUD" else "Lock"
        print(f"\n{cls.COLORS['bold']}{cls.COLORS['magenta']}Executing: {command.upper()}{cls.COLORS['end']}")
        print(f"{cls.COLORS['cyan']}   Mode: {mode_icon} {mode}{cls.COLORS['end']}")
        print(f"{cls.COLORS['cyan']}{'─' * 50}{cls.COLORS['end']}")

    @classmethod
    def format_response(cls, response: Dict[str, Any]) -> str:
        if not response:
            return cls.colorize("Empty response", "red")
        status = response.get('status', 'unknown')
        status_color = 'green' if status == 'success' else 'red' if status == 'error' else 'yellow'
        output = [f"{cls.COLORS['bold']}Status: {cls.colorize(status.upper(), status_color)}{cls.COLORS['end']}"]
        for key, value in response.items():
            if key != 'status':
                if isinstance(value, dict):
                    output.append(f"{cls.COLORS['bold']}{key}:{cls.COLORS['end']}")
                    for sk, sv in value.items():
                        output.append(f"  {cls.colorize(sk, 'cyan')}: {sv}")
                else:
                    output.append(f"{cls.COLORS['bold']}{key}:{cls.COLORS['end']} {value}")
        return '\n'.join(output)


class SmartParser:
    """Гибкий парсер + help без warning"""

    COMMAND_MAP = {
        # === ВЫБОР УСТРОЙСТВА ===
        'device': '--device', 'd': '--device', 'dev': '--device',
        
        # === ОСНОВНЫЕ КОМАНДЫ УСТРОЙСТВ ===
        'info': '--info', 'i': '--info', 'information': '--info', 'status': '--info',
        'ping': '--ping', 'p': '--ping', 'test': '--ping',
        'wake': '--wake', 'w': '--wake', 'wol': '--wake', 'wakeonlan': '--wake',
        'restart': '--restart', 'r': '--restart', 'reboot': '--restart', 'reset': '--restart',
        'ota': '--ota-start', 'o': '--ota-start', 'update': '--ota-start', 'upgrade': '--ota-start',
        'setup': '--open-setup', 's': '--open-setup', 'config-mode': '--open-setup',
        
        # === ВЕБ-СЕРВЕР ===
        'site-on': '--enable-site', 'enable-site': '--enable-site', 'web-on': '--enable-site',
        'site-off': '--disable-site', 'disable-site': '--disable-site', 'web-off': '--disable-site',
        'site': '--site-status', 'site-status': '--site-status', 'web-status': '--site-status',
        
        # === КРИПТОГРАФИЯ ===
        'crypto': '--crypto-info', 'crypto-info': '--crypto-info', 'security': '--crypto-info',
        
        # === УПРАВЛЕНИЕ УСТРОЙСТВАМИ ===
        'list': '--list-devices', 'ls': '--list-devices', 'l': '--list-devices',
        'add': '--add-device', 'add-device': '--add-device',
        'remove': '--remove-device', 'rm': '--remove-device', 'delete': '--remove-device',
        
        # === ПОМОЩЬ ===
        'help': '--help', 'h': '--help', '?': '--help',
    }

    def __init__(self):
        self.parser = self._build_parser()
        self.dev_mgr = DeviceManager()

    def _build_parser(self):
        p = argparse.ArgumentParser(
            add_help=False, 
            allow_abbrev=False,
            usage="%(prog)s [OPTIONS] [COMMAND]"
        )
        
        # Основные параметры
        p.add_argument("--device", "-d", help="Device name")
        p.add_argument("--ip", help="IP address")
        p.add_argument("--port", type=int, default=99, help="Port (default: 99)")
        p.add_argument("--token", "-t", help="Device token")
        p.add_argument("--api-token", "-a", help="API token")
        p.add_argument("--device-id", help="Device ID")
        p.add_argument("--cloud", "-c", action="store_true", help="Cloud mode")
        
        # Управление устройствами
        p.add_argument("--add-device", metavar="NAME", help="Add device")
        p.add_argument("--remove-device", metavar="NAME", help="Remove device")
        p.add_argument("--list-devices", action="store_true", help="List devices")
        
        # Основные команды устройств
        p.add_argument("--ping", action="store_true")
        p.add_argument("--info", action="store_true")
        p.add_argument("--wake", metavar="MAC")
        p.add_argument("--restart", action="store_true")
        p.add_argument("--ota-start", action="store_true")
        p.add_argument("--open-setup", action="store_true")
        
        # Веб-сервер
        p.add_argument("--enable-site", action="store_true")
        p.add_argument("--disable-site", action="store_true")
        p.add_argument("--site-status", action="store_true")
        
        # Криптография
        p.add_argument("--crypto-info", action="store_true")
        
        # Помощь
        p.add_argument("--help", "-h", action="store_true", help="Show help")
        
        return p

    def parse(self, args: List[str]):
        # Check for help first
        if any(arg in ['help', '--help', '-h'] for arg in args):
            return argparse.Namespace(help=True)
        
        # Если нет аргументов - показываем help
        if not args:
            return argparse.Namespace(help=True)

        parsed = argparse.Namespace()
        remaining = []
        i = 0
        
        # Флаги для отслеживания состояний
        expect_device_name = False
        expect_wake_mac = False
            
        while i < len(args):
            arg = args[i]

            if arg in ['help', '--help', '-h']:
                parsed.help = True
                i += 1
                continue

            if arg.startswith('-'):
                remaining.append(arg)
                i += 1
                continue

            # Обработка команд выбора устройства
            if arg in ['device', 'd', 'dev']:
                expect_device_name = True
                i += 1
                continue

            # Если ожидаем имя устройства
            if expect_device_name:
                parsed.device = arg
                expect_device_name = False
                i += 1
                continue

            # Обработка команды wake с MAC-адресом
            if expect_wake_mac:
                parsed.wake = arg
                expect_wake_mac = False
                i += 1
                continue

            # Обычные команды
            cmd = self.COMMAND_MAP.get(arg.lower())
            if cmd:
                attr_name = cmd.lstrip('-').replace('-', '_')
                setattr(parsed, attr_name, True)
                
                # Для команды wake - следующее слово это MAC-адрес
                if cmd == '--wake':
                    expect_wake_mac = True
                i += 1
                continue

            # Если это может быть имя устройства (когда используется флаг -d/--device)
            if not hasattr(parsed, 'device') or not parsed.device:
                if self.dev_mgr.get(arg):
                    parsed.device = arg
                    i += 1
                    continue

            # Если неизвестная команда - добавляем в remaining для стандартного парсера
            remaining.append(arg)
            i += 1

        # Парсим оставшиеся аргументы через argparse
        try:
            flag_args, unknown = self.parser.parse_known_args(remaining)
            for k, v in vars(flag_args).items():
                if v is not None and v != False and v != []:
                    setattr(parsed, k, v)
        except SystemExit:
            # Если argparse завершился с ошибкой, показываем help
            return argparse.Namespace(help=True)

        # Если указано устройство но нет команды - ошибка
        if hasattr(parsed, 'device') and parsed.device and not self._has_device_command(parsed):
            print(f"\n{OutputFormatter.COLORS['red']}Error: Device '{parsed.device}' specified but no command given{OutputFormatter.COLORS['end']}")
            print(f"{OutputFormatter.COLORS['yellow']}Usage: wl -d DEVICE <command>{OutputFormatter.COLORS['end']}")
            print(f"{OutputFormatter.COLORS['yellow']}Examples: wl d {parsed.device} info, wl device {parsed.device} ping{OutputFormatter.COLORS['end']}")
            return argparse.Namespace(help=True)

        return parsed

    def _has_device_command(self, parsed):
        """Проверяет есть ли команда для устройства"""
        device_commands = [
            'ping', 'info', 'wake', 'restart', 'ota_start', 'open_setup',
            'enable_site', 'disable_site', 'site_status', 'crypto_info'
        ]
        return any(getattr(parsed, cmd, False) for cmd in device_commands)

    @staticmethod
    def show_help():
        print("""
\033[1;36mWakeLink CLI v2.0 - Smart & Flexible\033[0m

\033[1;32mBASIC USAGE:\033[0m
  \033[33mwl\033[0m                              → This help screen
  \033[33mwl help\033[0m                         → Same

\033[1;32mDEVICE SELECTION (choose one format):\033[0m
  \033[33mwl -d DEVICE COMMAND\033[0m           → Short flag
  \033[33mwl --device DEVICE COMMAND\033[0m     → Long flag  
  \033[33mwl d DEVICE COMMAND\033[0m            → Command form
  \033[33mwl device DEVICE COMMAND\033[0m       → Command form

\033[1;32mDEVICE COMMANDS:\033[0m

\033[1;34m● Information:\033[0m
  \033[33minfo, i, information, status\033[0m    → Device information

\033[1;34m● Connectivity:\033[0m  
  \033[33mping, p, test\033[0m                   → Ping device
  \033[33mrestart, r, reboot, reset\033[0m       → Restart device

\033[1;34m● Wake-on-LAN:\033[0m
  \033[33mwake MAC, w MAC, wol MAC\033[0m        → Wake device by MAC

\033[1;34m● Updates:\033[0m
  \033[33mota, o, update, upgrade\033[0m         → OTA update

\033[1;34m● Configuration:\033[0m
  \033[33msetup, s, config-mode\033[0m           → Open setup AP
  \033[33mcrypto, crypto-info, security\033[0m   → Crypto info

\033[1;34m● Web Server:\033[0m
  \033[33msite-on, enable-site, web-on\033[0m    → Enable web server
  \033[33msite-off, disable-site, web-off\033[0m → Disable web server  
  \033[33msite, site-status, web-status\033[0m   → Web server status

\033[1;32mDEVICE MANAGEMENT:\033[0m
  \033[33mwl --list-devices, wl -l, wl list, wl ls\033[0m → List devices
  \033[33mwl --add-device NAME --ip IP --token TOKEN\033[0m
  \033[33mwl --remove-device NAME, wl remove NAME\033[0m

\033[1;32mEXAMPLES:\033[0m

\033[90m# All valid formats for device info:\033[0m
  \033[33mwl d esp info\033[0m                   
  \033[33mwl device esp information\033[0m       
  \033[33mwl -d esp i\033[0m                     
  \033[33mwl --device esp status\033[0m          

\033[90m# All valid formats for wake command:\033[0m
  \033[33mwl d esp wake AA:BB:CC:DD:EE:FF\033[0m 
  \033[33mwl -d esp w AA:BB:CC:DD:EE:FF\033[0m   
  \033[33mwl device esp wol AA:BB:CC:DD:EE:FF\033[0m 

\033[90m# Other commands:\033[0m
  \033[33mwl d esp restart\033[0m                
  \033[33mwl device esp crypto\033[0m            
  \033[33mwl -d esp ota\033[0m                   

\033[90m# Device management:\033[0m
  \033[33mwl --list-devices\033[0m                
  \033[33mwl -l\033[0m                            
  \033[33mwl list\033[0m                          
""")


class WakeLinkClient:
    def __init__(self):
        self.dev_mgr = DeviceManager()
        self.formatter = OutputFormatter()

    def _resolve_device(self, args):
        if not getattr(args, 'device', None) and not any([
            getattr(args, 'add_device', None),
            getattr(args, 'remove_device', None),
            getattr(args, 'list_devices', False),
            getattr(args, 'help', False)
        ]):
            return None

        dev = {
            "ip": getattr(args, 'ip', None),
            "port": getattr(args, 'port', 99) if getattr(args, 'port', None) is not None else 99,
            "token": getattr(args, 'token', None),
            "api_token": getattr(args, 'api_token', None),
            "cloud": getattr(args, 'cloud', False),
            "device_id": getattr(args, 'device_id', None),
        }

        if getattr(args, 'device', None):
            saved = self.dev_mgr.get(args.device)
            if not saved:
                self.formatter.print_error(f"Device '{args.device}' not found")
                return None
            dev.update(saved)
            self.formatter.print_success(f"Using saved device: {args.device}")

        if not dev["device_id"] and getattr(args, 'device', None):
            dev["device_id"] = args.device

        return dev

    def run(self, args):
        # === HELP ===
        if getattr(args, 'help', False):
            SmartParser.show_help()
            return

        # === LIST ===
        if getattr(args, 'list_devices', False):
            self.dev_mgr.list()
            return

        # === ADD / REMOVE ===
        if getattr(args, 'add_device', None):
            if not getattr(args, 'token', None):
                self.formatter.print_error("--token required")
                return
            if getattr(args, 'cloud', False) and not getattr(args, 'api_token', None):
                self.formatter.print_error("--api-token required")
                return
            if not getattr(args, 'cloud', False) and not getattr(args, 'ip', None):
                self.formatter.print_error("--ip required")
                return

            self.dev_mgr.add(
                name=args.add_device,
                ip=getattr(args, 'ip', None),
                token=args.token,
                api_token=getattr(args, 'api_token', None),
                port=getattr(args, 'port', 99),
                cloud=getattr(args, 'cloud', False),
                device_id=getattr(args, 'device_id', args.add_device)
            )
            self.formatter.print_success(f"Device '{args.add_device}' added")
            return

        if getattr(args, 'remove_device', None):
            self.dev_mgr.remove(args.remove_device)
            self.formatter.print_success(f"Device '{args.remove_device}' removed")
            return

        # === DEVICE COMMANDS ===
        dev = self._resolve_device(args)
        if not dev or not dev.get("token"):
            self.formatter.print_warning("No command - use 'wl help'")
            return

        handler_cls = CloudClient if dev["cloud"] else TCPHandler
        handler_kwargs = {"token": dev["token"], "device_id": dev["device_id"] or "python_client"}
        if not dev["cloud"]:
            if not dev["ip"]:
                self.formatter.print_error("IP required for local")
                return
            handler_kwargs.update({"ip": dev["ip"], "port": dev["port"]})
        if dev["cloud"]:
            if not dev.get("api_token"):
                self.formatter.print_error("API token required for cloud")
                return
            handler_kwargs["api_token"] = dev["api_token"]

        handler = handler_cls(**handler_kwargs)
        mode = "CLOUD" if dev["cloud"] else "LOCAL"
        self.formatter.print_info(f"{mode} mode activated")

        client = WakeLinkCommands(handler)

        cmd_map = {
            "ping": client.ping_device,
            "wake": client.wake_device,
            "info": client.device_info,
            "restart": client.restart_device,
            "ota_start": client.ota_start,
            "open_setup": client.open_setup,
            "enable_site": client.enable_site,
            "disable_site": client.disable_site,
            "site_status": client.site_status,
            "crypto_info": client.crypto_info,
        }

        executed = False
        
        # Сначала проверяем команду wake (она требует специальной обработки)
        if hasattr(args, 'wake') and args.wake:
            self.formatter.print_command("wake", mode)
            try:
                result = client.wake_device(format_mac_address(args.wake))
                print(f"\n{self.formatter.format_response(result)}")
                executed = True
            except Exception as e:
                self.formatter.print_error(f"Wake failed: {e}")

        # Затем проверяем остальные команды
        for cmd, func in cmd_map.items():
            if cmd != "wake" and getattr(args, cmd, False):  # исключаем wake из общего цикла
                self.formatter.print_command(cmd, mode)
                try:
                    result = func()
                    if result:
                        print(f"\n{self.formatter.format_response(result)}")
                    executed = True
                except Exception as e:
                    self.formatter.print_error(f"Failed: {e}")
                break
        if not executed:
            self.formatter.print_warning("No command - use 'wl help'")


def main():
    parser = SmartParser()
    args = parser.parse(sys.argv[1:])

    try:
        client = WakeLinkClient()
        client.run(args)
    except KeyboardInterrupt:
        print(f"\n{OutputFormatter.colorize('Cancelled', 'yellow')}")
    except Exception as e:
        OutputFormatter.print_error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()