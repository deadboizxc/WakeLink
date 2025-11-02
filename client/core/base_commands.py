from abc import ABC, abstractmethod

class BaseCommands(ABC):
    """Базовый интерфейс команд для всех клиентов"""
    
    @abstractmethod
    def ping_device(self): 
        """Проверка связи с устройством"""
        pass
    
    @abstractmethod
    def wake_device(self, mac): 
        """Отправка WOL пакета"""
        pass
    
    @abstractmethod
    def device_info(self): 
        """Получение информации об устройстве"""
        pass
    
    @abstractmethod
    def restart_device(self): 
        """Перезагрузка устройства"""
        pass
    
    @abstractmethod
    def ota_start(self): 
        """Запуск OTA обновления"""
        pass

    def open_setup(self): 
        return {"status": "error", "error": "Not supported"}
    
    def enable_site(self): 
        return {"status": "error", "error": "Not supported"}
    
    def disable_site(self): 
        return {"status": "error", "error": "Not supported"}
    
    def site_status(self): 
        return {"status": "error", "error": "Not supported"}
    
    def crypto_info(self): 
        return {"status": "error", "error": "Not supported"}