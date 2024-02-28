import cy_kit
from cyx.common.global_settings_services import GlobalSettingsService

from cyx.media.contents import ContentsServices


class GeminiService:
    def __init__(self,
                 global_settings_service=cy_kit.singleton(GlobalSettingsService),
                 contents_service=cy_kit.singleton(ContentsServices)
                 ):
        self.global_settings_service = global_settings_service
        self.contents_service = contents_service

    def get_text(self, file_path: str | None, is_image: bool, text: str):
        if not is_image:
            content = self.contents_service.get_text(file_path)
        pass
