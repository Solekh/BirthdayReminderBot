
import json
from datetime import datetime
from pathlib import Path
from os.path import join
import aiofiles

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = join(BASE_DIR, 'db')

class Birthday:
    def __init__(self, id: int = None, name: str = None, birthdate: str = None, photo: str = None):
        self.id = id
        self.name = name
        self.birthdate = birthdate
        self.photo = photo

    @property
    async def objects(self):
        file_name = self.__class__.__name__.lower() + "s.json"
        async with aiofiles.open(join(DB_PATH, file_name), 'r') as f:
            data = await f.read()
            data = json.loads(data)
        return [self.__class__(**i) for i in data]

    async def write(self, data):
        file_name = self.__class__.__name__.lower() + "s.json"
        async with aiofiles.open(join(DB_PATH, file_name), 'w') as f:
            await f.write(json.dumps([i.__dict__ for i in data], indent=3))

    async def save(self, default: bool = False):
        objects = await self.objects
        if not default:
            self.id = objects[-1].id + 1 if objects else 1
        objects.append(self)
        await self.write(objects)

    async def get_user_by_id(self, id):
        data = await self.objects
        for user in data:
            if user.id == int(id):
                return user
        return None

    async def search_user_by_name(self, name):
        data = await self.objects
        return [user for user in data if name.lower() in user.name.lower()]

    async def delete(self, id):
        objects = await self.objects
        objects = [obj for obj in objects if obj.id != int(id)]
        await self.write(objects)

    async def check_today_birthdays(self):
        today = datetime.now().strftime("%m-%d")
        return [user for user in await self.objects if user.birthdate[5:] == today]

    async def update(self, **fields):
        objects = await self.objects
        for obj in objects:
            if obj.id == self.id:
                for k, v in fields.items():
                    setattr(obj, k, v)
                await self.write(objects)
                return obj
