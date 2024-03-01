import gc
import json
import math

import cy_kit
from cyx.common.global_settings_services import GlobalSettingsService

from cyx.media.contents import ContentsServices
import google.generativeai as genai
import PIL.Image
import os


class GeminiService:
    def __init__(self,
                 global_settings_service=cy_kit.singleton(GlobalSettingsService),
                 contents_service=cy_kit.singleton(ContentsServices)
                 ):
        self.global_settings_service = global_settings_service
        self.contents_service = contents_service

    def estimate_token_size(self, text, method="word"):
        """
        Estimates the number of tokens in a sentence using the specified method.

        Args:
            text: The text to estimate the token size for.
            method: The tokenization method to use. Can be "word" or "subword".

        Returns:
            The estimated number of tokens.
        """

        if method == "word":
            # Word-based tokenization
            tokens = text.split()
            return len(tokens)
        elif method == "subword":
            # Sub-word tokenization (example using spaCy)
            import spacy
            nlp = spacy.load("en_core_web_sm")  # Load a suitable spaCy model
            doc = nlp(text)
            return len(doc)
        else:
            raise ValueError("Invalid tokenization method. Choose 'word' or 'subword'.")

    def text_prompt(self, file_path, question:str):
        genai.configure(api_key=self.global_settings_service.get_gemini_key())
        model = genai.GenerativeModel("gemini-pro")
        ref_content = self.get_text_from_tika(file_path)
        running_text = question.replace("@{file}",'"'+ ref_content+'"')
        response = model.generate_content(running_text, stream=True)
        response.resolve()
        return response.text

    def image_prompt(self, file_path, question):
        genai.configure(api_key=self.global_settings_service.get_gemini_key())
        img = self.load_image_for_gemini(file_path)
        model = genai.GenerativeModel("gemini-pro-vision")
        response = model.generate_content([
            question,
            img], stream=True)
        response.resolve()
        del img
        gc.collect()
        return response.text

    def get_text(self, format_content: str | None, question: str | None,
                 output: str = "text", file_path: str | None = None, is_image: bool = False):
        genai.configure(api_key=self.global_settings_service.get_gemini_key())
        if isinstance(file_path, str):
            if not is_image:
                ref_content = self.get_text_from_tika(file_path)
                command_text = output + " format that content "
                if isinstance(format_content, str):
                    command_text += "by following format " + format_content
                if isinstance(question, str) and len(question) > 0:
                    command_text = question
                model = genai.GenerativeModel("gemini-pro")
                running_text = '"' + ref_content + '"' + "\n" + command_text
                response = model.generate_content(running_text, stream=True)
                response.resolve()
                if output.lower() == "json":
                    return self.convert_json_text_to_dict(response.text)

                return response.text
            else:
                command_text = " do OCR and get all text in that image"
                if isinstance(format_content, str):
                    command_text += " and format  by below JSON " + format_content
                if isinstance(question, str) and len(question) > 0:
                    command_text = question
                img = self.load_image_for_gemini(file_path)
                model = genai.GenerativeModel("gemini-pro-vision")
                response = model.generate_content([
                    command_text,
                    img], stream=True)
                response.resolve()
                del img
                gc.collect()
                if output.lower() == "json":
                    return self.convert_json_text_to_dict(response.text)
                return response.text
        elif isinstance(question, str):
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(question, stream=True)
            response.resolve()
            return response.text

    def load_image_for_gemini(self, file_path, max_size=4194304) -> PIL.Image:

        image = PIL.Image.open(file_path)
        if os.path.getsize(file_path) > max_size:
            scale_factor = 1 - float(os.path.getsize(file_path) - max_size) / float(os.path.getsize(file_path))
            width, height = image.size
            # Calculate new dimensions (rounded to nearest integer)
            new_width = round(width * scale_factor)
            new_height = round(height * scale_factor)

            # Resize the image using the ANTIALIAS filter for smoother scaling
            resized_image = image.resize((new_width, new_height), resample=PIL.Image.LANCZOS).convert("RGB")
            return resized_image
        else:
            return image

    def get_raw_text(self, file_path):
        genai.configure(api_key=self.global_settings_service.get_gemini_key())
        img = self.load_image_for_gemini(file_path)
        model = genai.GenerativeModel("gemini-pro-vision")
        response = model.generate_content([
            "extract all text of that image",
            img], stream=True)
        response.resolve()
        del img
        gc.collect()
        return response.text

    def get_json_text(self, text_content):
        """
          Finds and extracts the text between the first and last curly braces in a string, including the braces.

          Args:
              text_content: The string to search.

          Returns:
              The extracted text containing the content between the first and last curly braces, or None if none are found.
          """

        if not text_content:
            return None

        first_index, last_index = self.find_first_and_last_curly_braces(text_content)

        if first_index is not None and last_index is not None:
            # Extract the text including braces (slice up to but not including last_index + 1)
            return text_content[first_index: last_index + 1]
        else:
            return None

    def find_first_and_last_curly_braces(self, text_content):
        """
          Finds the first and last occurrences of curly braces ({ and }) in a string.

          Args:
              text_content: The string to search.

          Returns:
              A tuple containing the first and last indices of the curly braces, or None if none are found.
          """

        if not text_content:
            return None, None

        first_index = None
        last_index = None

        # Use a loop to iterate through characters
        for i, char in enumerate(text_content):
            if char == "{":
                if first_index is None:
                    first_index = i
            elif char == "}":
                last_index = i

        # Return only if both first and last indices are found
        if first_index is not None and last_index is not None:
            return first_index, last_index
        else:
            return None, None

    def convert_json_text_to_dict(self, text):
        try:
            json_text = self.get_json_text(text)
            ret = json.loads(json_text)
            return ret
        except:
            return text

    def get_text_from_tika(self, file_path):
        ref_content, meta = self.contents_service.get_text(file_path)
        ref_content = ref_content.lstrip(' ').rstrip(' ')
        ref_content = ref_content.lstrip('\n').rstrip('\n')
        ref_content = ref_content.lstrip(' ').rstrip(' ')
        ref_content = ref_content.lstrip('\n').rstrip('\n')
        while "\n\n" in ref_content:
            ref_content = ref_content.replace("\n\n", "\n")
        while "\r\r" in ref_content:
            ref_content = ref_content.replace("\r\r", "\n")
        while "  " in ref_content:
            ref_content = ref_content.replace("  ", " ")
        return ref_content
