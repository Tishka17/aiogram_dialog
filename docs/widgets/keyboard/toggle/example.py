@dataclass
class Fruit:
    id: str
    name: str
    emoji: str


async def get_fruits(**kwargs):
    return {
        "fruits": [
            Fruit("apple_a", "Apple", "🍏"),
            Fruit("banana_b", "Banana", "🍌"),
            Fruit("orange_o", "Orange", "🍊"),
            Fruit("pear_p", "Pear", "🍐"),
        ],
    }


dialog = Dialog(
    Window(
        Const("Toggle widget"),
        Toggle(
            Format("{item.emoji} {item.name}"),
            id="radio",
            items="fruits",
            item_id_getter=lambda fruit: fruit.id,
        ),
        state=ToggleExampleSG.START,
        getter=get_fruits,
    ),
)