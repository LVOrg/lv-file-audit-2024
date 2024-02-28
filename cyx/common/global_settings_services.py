import datetime

import cy_kit
from cyx.repository import Repository
from cyx.cache_service.memcache_service import MemcacheServices


class GlobalSettingsService:
    def __init__(self, cacher=cy_kit.singleton(MemcacheServices)):
        self.cacher = cacher
        self.GEMINI_API_KEY = f"{type(self).__module__}.{type(self).__name__}.GEMINI_API_KEY"

    async def update_or_create_async(self,
                                     ai_gemini_key: str | None,
                                     ai_gemini_descrition: str | None,
                                     ai_gpt_key: str | None,
                                     ai_gpt_description: str | None):
        global_settings_context = Repository.global_settings.app('admin')

        ret = await global_settings_context.context.find_one_async({})
        filter = Repository.global_settings.fields.id != None

        if ret is None:
            await global_settings_context.context.insert_one_async(
                Repository.global_settings.fields.AI.Gemini.Key << ai_gemini_key,
                Repository.global_settings.fields.AI.Gemini.Description << ai_gemini_descrition,
                Repository.global_settings.fields.AI.Gemini.CreatedOn << datetime.datetime.utcnow(),
                Repository.global_settings.fields.AI.GPT.Key << ai_gpt_key,
                Repository.global_settings.fields.AI.GPT.Description << ai_gpt_description,
                Repository.global_settings.fields.AI.GPT.CreatedOn << datetime.datetime.utcnow()
            )
        else:
            await global_settings_context.context.update_async(
                filter,
                Repository.global_settings.fields.AI.Gemini.Key << ai_gemini_key,
                Repository.global_settings.fields.AI.Gemini.Description << ai_gemini_descrition,
                Repository.global_settings.fields.AI.Gemini.ModifiedOn << datetime.datetime.utcnow(),
                Repository.global_settings.fields.AI.GPT.Key << ai_gpt_key,
                Repository.global_settings.fields.AI.GPT.Description << ai_gpt_description,
                Repository.global_settings.fields.AI.GPT.ModifiedOn << datetime.datetime.utcnow()
            )
        ret = await global_settings_context.context.find_one_async({})
        self.cacher.set_str(self.GEMINI_API_KEY, ai_gemini_key)
        return ret

    def get_gemini_key(self) -> str | None:
        ret = self.cacher.get_str(self.GEMINI_API_KEY)
        if ret is None:
            global_settings_context = Repository.global_settings.app('admin')
            ret = global_settings_context.context.find_one({})
            key_value = ret[Repository.global_settings.fields.AI.Gemini.Key]
            self.cacher.set_str(self.GEMINI_API_KEY,key_value)
            ret = self.cacher.get_str(self.GEMINI_API_KEY)
        return ret

