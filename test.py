from src import Settler, WoodSettler

if __name__ == '__main__':

    settler = Settler("Pioneer")
    print(f"Created settler with name: {settler.name} {(settler.__class__.__name__)}")

    settler.wear_clothes()
    print(f"{settler.name} wears {settler.clothes}")

    settler.locate()
    print(f"{settler.name} is at {settler.coordinates}")

    # Dynamically reassign class
    settler.__class__ = WoodSettler
    print(f"Settler is now a wood settler with name: {settler.name} {(settler.__class__.__name__)}")
    settler.init_as_wood_settler()
    print(f"Wood carried initially : {settler.wood_carried}")

    settler.wear_clothes()
    print(f"{settler.name} wears {settler.clothes}")

    settler.bear_tools()
    print(f"{settler.name} carries tools : {settler.tools} and is at {settler.coordinates}")

    settler.__class__ = Settler
    print(f"Wood settler with name : {settler.name} no longer limited to wood chopping {(settler.__class__.__name__)}")