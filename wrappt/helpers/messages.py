# TODO: Expand to make a connector to be able to store and retrieve that data from the DB
from pydantic import BaseModel
from typing import List, Dict
import copy


class MessagesManager(BaseModel):
    history_messages: List[Dict]

    def get_history(self):
        return self.history_messages
    
    def add_message(self, role: str, content: str):
        if role not in {"user", "assistant"}:
            raise KeyError("The role needs to be either user or assistant")
        
        new_message ={
                "role": role,
                "content": content
            }
        
        self.history_messages.append(new_message)

    def copy_history(self):
        return MessagesManager(history_messages=copy.deepcopy(self.history_messages))