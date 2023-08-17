from abc import ABC, abstractmethod


class IRepository(ABC):
    @abstractmethod
    def find_all(self):
        raise NotImplementedError

    @abstractmethod
    def find_all_pageable(self, page, rows_per_page: int = 5):
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, item_id: int):
        raise NotImplementedError

    @abstractmethod
    def create(self, *args):
        raise NotImplementedError

    @abstractmethod
    def update(self, item):
        raise NotImplementedError

    @abstractmethod
    def delete(self, item_id: int):
        raise NotImplementedError
