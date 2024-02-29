import cy_kit
from cyx.common.global_settings_services import GlobalSettingsService

from cyx.media.contents import ContentsServices
import google.generativeai as genai


class GeminiService:
    def __init__(self,
                 global_settings_service=cy_kit.singleton(GlobalSettingsService),
                 contents_service=cy_kit.singleton(ContentsServices)
                 ):
        self.global_settings_service = global_settings_service
        self.contents_service = contents_service

    def get_text(self, file_path: str | None, is_image: bool, text: str):
        genai.configure(api_key=self.global_settings_service.get_gemini_key())
        if not is_image:
            ref_content, meta = self.contents_service.get_text(file_path)
            command_text = "JSON format that content"
            if text is not None and isinstance(text,str):
                command_text+= "by following format "+text
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content('"' + ref_content + '"' + "\n" + command_text, stream=True)
            response.resolve()

            return response.text
        else:
            model = genai.GenerativeModel("gemini-pro-vision")
