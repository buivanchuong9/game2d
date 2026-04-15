# shop.py
# Quản lý shop, các hàm lấy card shop, item shop, xử lý mua bán
import random

SHOP_CARD_SURFACES = {}
def get_random_shop_card():
    if SHOP_CARD_SURFACES:
        return random.choice(list(SHOP_CARD_SURFACES.values()))
    return None

def get_random_pet_card():
    pet_cards = [k for k in SHOP_CARD_SURFACES if "Pet" in k]
    if pet_cards:
        return SHOP_CARD_SURFACES[random.choice(pet_cards)]
    return None
#code for the shop system
class Shop:
    def __init__(self):
        # Khoi tao cua hang voi cac vat pham co ban
        self.items = ["Hoi mau", "Tang toc", "Vu khi moi"]

    def display_items(self):
        # Hien thi cac vat pham cua hang
        for idx, item in enumerate(self.items, start=1):
            print(f"{idx}. {item}")

    def buy_item(self, item_number):
        # Xu ly viec mua hang
        if 0 < item_number <= len(self.items):
            print(f"Ban da mua {self.items[item_number - 1]}")
        else:
            print("Lua chon khong hop le.")
