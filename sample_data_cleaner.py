from os import scandir
import json
import unicodedata


def convert_all():
    combined_dataset = []
    with scandir("tests/sample_data") as dir_entries:
        for entry in dir_entries:
            # print(f"entry: {entry}")
            combined_dataset.append(convert(f"tests/sample_data/{entry.name}"))

    with open("tests/full-dataset3.json", "w") as f:
        json.dump(combined_dataset, f)


def convert(filename):
    with open(filename) as f:
        json_data = json.load(f)
        if json_data["name"] == "Dairy-Free Heavy Cream":
            print("breakpoint")
        for ingredient in json_data["ingredients"]:
            if "amount" in ingredient and ingredient["amount"] is not None:
                if len(ingredient["amount"]) == 3:
                    if ingredient["amount"] in my_3char_dict:
                        ingredient["amount"] = my_3char_dict[ingredient["amount"]]
                    else:
                        # print(ingredient)
                        try:
                            ingredient["amount"] = float(
                                ingredient["amount"][0]
                            ) + unicodedata.numeric(ingredient["amount"][2])
                        except ValueError as err:
                            print(
                                f"Parsing error for {ingredient} in {json_data['original_url']}"
                            )

                elif (
                    len(ingredient["amount"]) == 5
                    and (
                        ingredient["amount"][1] == " " or ingredient["amount"][1] == "-"
                    )
                    and (
                        ingredient["amount"][3] == "/"
                        or ingredient["amount"][3] == "\u2044"
                    )
                ):
                    num = unicodedata.numeric(ingredient["amount"][0])
                    fraction = ingredient["amount"][2] + "/" + ingredient["amount"][4]
                    if fraction in my_3char_dict:
                        ingredient["amount"] = num + my_3char_dict[fraction]
                elif len(ingredient["amount"]) == 1:
                    try:
                        ingredient["amount"] = float(ingredient["amount"])
                    except ValueError:
                        ingredient["amount"] = unicodedata.numeric(ingredient["amount"])

            if ingredient["ingred_name"] is None:
                print(f"Parsing error for {ingredient} in {json_data['original_url']}")
        return json_data


my_3char_dict = {
    "1/2": 0.5,
    "1/3": 0.333,
    "1/4": 0.25,
    "2/3": 0.666,
    "3/4": 0.75,
    "1/5": 0.2,
    "2/5": 0.4,
    "3/5": 0.6,
    "4/5": 0.8,
    "1/6": 0.166,
    "1/7": 0.142,
    "1/8": 0.125,
}

convert_all()
