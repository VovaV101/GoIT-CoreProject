from __future__ import annotations

import json
from collections import UserDict
from typing import Generator

from save_data.save_base import SaveBase
from src.record import Record, RecordAlreadyExistsException


class AddressBook(UserDict):
    """
    Class that describes the logic of saving client's records in the address book and
    making manipulations with the records.
    """

    def __init__(self, data_save_tool: SaveBase):
        super().__init__()
        self.data_save_tool = data_save_tool
        self.data.update(self.data_save_tool.read_info(path=self.data_save_tool.address))

    def iterator(self, record_num: int = None) -> Generator:
        """
        Method that implements the logic of the generator to retrieve records from the
        Address Book by chunks.
        :param record_num: The size of chunks of the records from the Address Book.
        :return: Generator.
        """
        address_book: dict = self.data_save_tool.read_info(
            path=self.data_save_tool.address)
        book_items = list(address_book.items())
        if not record_num:
            step = 1
        else:
            step = record_num
        for i in range(0, len(book_items), step):
            start = i
            stop = i + step
            yield book_items[start:stop]

    def add_record(self, record: Record) -> None:
        """
        Method adds Record objects into the address book using client name as a key
        and the object as a value.
        :param record: Record instance that has an information about client name and
        her/his phone numbers.
        """
        address_book: dict = self.data_save_tool.read_info(
            path=self.data_save_tool.address)
        if record.name.value not in address_book:
            self.data[record.name.value] = record
            record_data = repr(record)
            address_book.update(json.loads(record_data))
            self.data_save_tool.save_info(path=self.data_save_tool.address,
                                          data=address_book)
        else:
            raise RecordAlreadyExistsException(f"Record with the name '"
                                               f"{record.name.value}' already exists "
                                               f"in the address book dictionary")

    def update_record(self, record: Record) -> None:
        """
        Method makes record update in the data saving tool.
        :param record: Updated Record instance.
        :return: None.
        """
        address_book: dict = self.data_save_tool.read_info(
            path=self.data_save_tool.address)
        found_record = address_book.get(record.name.value)
        if found_record:
            address_book[record.name.value] = json.loads(repr(record))[record.name.value]
            self.data_save_tool.save_info(path=self.data_save_tool.address,
                                          data=address_book)
        else:
            raise ValueError(f"The contact with the name '{record.name.value}' has not"
                             f" been found in the Address Book")

    def find(self, name: str) -> Record:
        """
        Method finds records from the address book by client's name.
        :param name: The name of a client.
        :return: Record from the address book for specific client.
        """
        record: dict = self.data_save_tool.read_info(
            path=self.data_save_tool.address).get(name)
        if record:
            record_obj = Record(name=name, birthday=record.get("birthday"))
            for phone in record["phones"]:
                record_obj.add_phone(phone_num=phone)
            return record_obj
        else:
            return None

    def search_contact(self, search_phrase: str) -> Generator:
        """
        Method searches info about contact by name or phone using approximate equality.
        :param search_phrase: The phrase which is used for the searching contacts in the
        Address Book.
        """
        address_book: dict = self.data_save_tool.read_info(
            path=self.data_save_tool.address)
        for contact_name, contact_info in address_book.items():
            found_phones = list(filter(lambda phone: search_phrase in phone,
                                       contact_info["phones"]))
            if any([search_phrase.lower() in contact_name.lower(), found_phones]):
                yield {"name": contact_name, "info": contact_info}

    def delete(self, name: str) -> None:
        """
        Method deletes the record from the address book for the specific client by
        his/her name.
        :param name: Client's name.
        :return: None.
        """
        address_book: dict = self.data_save_tool.read_info(
            path=self.data_save_tool.address)
        record: dict = address_book.get(name)
        if record:
            self.data.pop(name)
            address_book.pop(name)
            self.data_save_tool.save_info(path=self.data_save_tool.address,
                                          data=address_book)
        else:
            raise ValueError(f"Contact with the name '{name}' doesn't exist in the "
                             f"Address Book")
