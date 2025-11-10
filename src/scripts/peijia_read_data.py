import os

# External
import pandas as pd
from dotenv import load_dotenv
import requests
import json

__all__ = ["get_object_library_data"]

load_dotenv()

API_ENDPOINT = os.getenv("API_ENDPOINT")
API_TOKEN = os.getenv("API_TOKEN")

pset_names = [
    "wall_layer_basic",
    "wall_layer_material",
    "wall_layer_construction"
]

row_entry_counts = {
    "12fZK9NQLfaJ42CtzpDeXY": 36,
    "I5yvQ7HE1Xza5FTLW071U0": 2,
    "EgMhhYhriZlv2NAolMQX7u": 2,
    "wkOnk6ZS8odSbf5QMJGKZd": 2,
    "d8zIV17St5BKAcW4eXsB7a": 2,
    "5S4jPLSCFpZQnKdcLQNzIn": 3,
    "O0f6jKc7GWzeFiBHUTSRm0": 3,
    "9wwtaZYEcz4FqhR2UsbViy": 3,
    "UI8FhsUQKciCqoV6GbOX5M": 3,
    "3LNwo8gSybAxcCVqHFTnnq": 4,
    "vf3kScKSYUkTrse6LeOT2n": 4,
    "uYannuVv4YBBtPpu9urYD2": 4,
    "s7ct3V4t9wbPUwhYXrMiPH": 4,
    "5Swco08JQqLgmIUIjmmo0Q": 4,
    "x2wS6N1nBRuS5aP9Yo4AH5": 14,
    "JzuKwWbEcQvVnlVKCrjzTh": 14,
    "ljgwVZnpsIgnXF8WaDoiye": 13,
    "WQCjfuWHennET9Pso4iqXv": 13,
    "9TztQ0l9JSIqtyhBSymLWQ": 5,
    "EAxA0wOz95EQfafBXDAw94": 11,
    "m5CG7pzifPEwR0t2mkNd7Q": 11,
    "w5YYR8hOBXukT0dyjHaiB4": 11,
    "BhqPk8KXoFDYJ1ivXcpw3q": 11,
    "nIMmi9oNTUorz1f7yqlY0W": 53,
    "b4Vakg6CSgrUbBW0ci4FOq": 53,
    "i8rTq2LLWWoJoqHRWVAcrm": 11,
    "iQNkdJciw64yElcsiXzdqV": 1,
    "UyAtNe1F3hpEuFlc512hEl": 11,
    "CpovJsCUmIHmoqJFftpm77": 4,
    "udcJh9qwr19Jjbb4iABkBs": 103,
    "ydSeUQAkDlxXrs6DVU0BJd": 1,
    "pTV2ec8uS89TirUWHLgCsL": 1,
    "SYElcK5El0cY9NX8aEYMmK": 1,
    "CHsvAWNXFOMjDcIsSAJH1g": 1,
    "yKiyMRJ3eItGGwxhxsgoKc": 1,
    "9hbHODygMBs1zSHlN1AOUA": 1,
    "jLdAhd260hvWdYpAd4tug9": 1,
    "kitwRvliOA24YZjMgjAb5a": 1,
    "FeTyocksjTXgti7rIWolKR": 2,
    "0bqb6QelhnRDepladwxCau": 2,
    "pVO6L7J1R1MtPIKhbuBzPx": 1,
    "tvcCzN5xcZUphk3GosqmwM": 2,
    "yn5bcDVqYdKzm9nSuBbZjq": 2,
    "A0fu8VDjM87LP4u368zofl": 2,
    "2H5H0TW02uCADuoIK1Rm9C": 2,
    "MMV469YhsmdGYs4PFv7DJ5": 2,
    "L7sHD7jHI0Kb4aYb9x4E7U": 2,
    "T0J7Roqqmu7puphNPFdym4": 2,
    "AlgQjGphoa7P5DFY2ET4f6": 4,
    "lCvSDpo28iVlvFJYie97rG": 43,
    "mZnxPTHH1ZGY5qmkBKLFxP": 43,
    "UXPOyGJ5kUxQgNvYKHJqeu": 23,
    "zwxeUOT1E0l8kCeC5aad56": 23,
    "5ylv1fTqfYWYZskRw9SKzX": 12,
    "R3XfMS0VjpM56Qv1aRpTQk": 12,
    "Fftpzcuv6DYaKYreZWdrxJ": 12,
    "VsOwqpsEfjq9ubxvRHHYcn": 51,
    "mOcexy7xnQ1fZMRoowgDE7": 51,
    "JwVmWLF3PW17wve399BDMO": 8,
    "uXwRUjJqgELQmasVSJgDJZ": 31,
    "t627ncJmj79rCEOL3uEfxY": 31,
    "Y1tiFJNz03oa3fkYBWFEwF": 10,
    "gItTJ12E5xqpVNcnO7sqeb": 10,
    "IHvoIbIbYGPlfCsFn7sety": 30,
    "yN1LdzGdsuych77kEWm3Ca": 30,
    "q2IQrMIal1uITy7T6FKosQ": 30,
    "HRxd3tERnYY7XBJ3ZjgIG1": 15,
    "d57svD8qUpabQofLdKpBlR": 25,
    "jP7c061duuFBBPuziM1oto": 25,
    "2s0E7qAc8yetFITYwQfcTT": 33,
    "RNSeioLBhEAKdUThjCC694": 33,
    "eOGBBmXhN9Tp8Yvljlo5U5": 33,
    "qPitYbFvKnFGfdaQI6hIqP": 33,
    "ABhgbXvt6Z0hrRC1eDmhdo": 33,
    "igkDg7NalHdVx8a0dDnrAl": 21,
    "6cHOvQVwgzdcyUJjpJxzgZ": 21,
    "E3bY7jlVxNjCnZeTnBApgb": 21,
    "3Beu5Pfng622K7CGakBX3F": 6,
    "9uA55HUTWNotr3AU8TtpXQ": 6,
    "39rhWi7GsUGCL6MFibEjyg": 6,
    "ZXcNChBK4DGpWovGsa6VHm": 6,
    "FG4xWUCH1bsZLFg0x7sTQV": 3,
    "vCQu9GYLZVgB5QAqlYxU3J": 3,
    "B7YvXXMtss5oAI9gCBvkRf": 2,
    "bDlBDIuQjyrpzcuX94MAO3": 2,
    "0OdxBLHGfRqLDIE3ESoi1k": 2,
    "NZSNkcnN1PEB0RBmR5J4cu": 2,
    "sRjwT9pdSyLA958ywErlUq": 2,
    "JckMG6k7XycguGIJsGSU0X": 26,
    "eWVUQydwPcTWW6IROnB7sM": 139,
    "CJaWKhcWivV0gshEDVrPg7": 139,
    "3j5HbiENkMCnkxdurmafqg": 5,
    "d3306pf4cog93YnqgO7leQ": 5,
    "xo8Vl81cexPCZSZ9ziUNIp": 2,
    "MS9F581xYWtwwCITlXxcA0": 2,
    "xUOVH2IdwkBQZKZH2lb0KK": 1,
    "sSqQE234hsUmrkAQvdoVKd": 2,
    "emklVGI0O2qQc0KkLc5GM1": 2,
    "kRHLgLjhD2POL0Zgiu0kjB": 5,
    "bQgpZMQ6YUhG5yGrjViOue": 5,
    "i7tHnviIvB2Y29ixEM4Lra": 27,
    "8Y51yddcQO4NJ2CG6ituxK": 5,
    "lczzSKxXQ9rQ1Z2rnD7Skm": 5,
    "9QNuAURzpPoX4obruavbMQ": 5,
    "dAOolf5lw4S8JwMBLdrA0q": 5,
    "54CChGEd9F79pJLS6dC4gK": 7,
    "QrGUscDIqCi0xDcp9Lg4uw": 7,
    "XggjrmMatO1VwRBk8qexJv": 4,
    "QIuTKOU9ogEmw0uP0Bsdg4": 1,
    "HkBAe2Q3LHL5whkWoOEoJD": 1,
    "QaVI97o5I6d4ArePeMW4YF": 5,
    "2I1rHiX1vqypwJ1NPpFdHr": 5,
    "7YiImRheoYbD4Sf4OmoKAR": 10,
    "RcKhyVmh7PSOdPU0P7bzfV": 5,
    "liQq25K93nE6nyAOoXzNaG": 5,
    "R3n4SOITsnWT5a0XC9t7Lg": 5,
    "77wJduZvGOjG6pKnDcICeJ": 8,
    "gBW2zWsJEOIlMhHenhjL7O": 8,
    "O14dAI1rWkCbgt7eV1ppnm": 8,
    "POYTaW2FZcAMGneo2Hd51i": 4,
    "0i3I8m07lgGrwNlYBjERuR": 4,
    "JQoyGFEQXnKSjka2iaawcN": 4,
    "W7lKoX8AazyJIKfahsxkAZ": 31,
    "soxlm8A0mrxLkaiMBOBFeB": 3,
    "RnTpEc1v7KJ4hNqzbHm4qH": 3,
    "iNknivug3oPYFEoYhPDEkh": 3,
    "ejF5Tsu8pYLPdUJhpsfHaj": 25,
    "lCWXgyyvwj6jkV07ttvt14": 25,
    "why4ebiz3e8X20UyEbSRth": 5,
    "ZKMA7PahdJb4cwmfPcV8MS": 5,
    "ul67UC1OjvaTqCLBll0ioe": 3,
    "CdwMGaH7d3LXfkvrXT5pBi": 3,
    "OCjfhnbSzpDLFduHAe9CJr": 1,
    "eDmAqtX4M6LVSkWMXcDuIJ": 42,
    "bXn7hYZnDdAKu3krp9PBLO": 7,
    "lEKn6Ippaetr5oK74dv2Dx": 2,
    "F9Gnp5acZjXt3dqwzmb03J": 2,
    "UaHlQgRajzwVjEqJBJNpk1": 9,
    "FkZuTIpVoNpgbsrRK7O2GM": 15,
    "aMHIA3UjPICLkuZfuxcO9m": 15,
    "Wj7xhSsTDTCYPan1T8SVfj": 1,
    "notkoN5ZbXdTvVAgIcNVej": 1,
    "YirKgMX8NgnZcQvwqQegqz": 1,
    "R5bR4JMBRPPVeO7bT6NWZF": 2,
    "SUnXSAH4KQtXZoBXfAoqpw": 7,
    "JKiqC4TFCtSGlwuzK8gMrb": 7,
    "288FZy6R4EVSi0ms8b6zb8": 7,
    "AddPryeGS76iSZtdToEzbW": 7,
    "LNeXM9JH6HCot9b9kfPvDK": 7,
    "azq5HXo7ZsMpf2RJJJDjeG": 1,
    "YtFsvUZPK2L9Pmv4ypqWKt": 1,
    "xGe7UuK96hnF0Sq51Qj4s5": 1,
    "YTdLsuETjV36vvQWsWQWkI": 1,
    "WavskKV0d5kHEt7Ynnxxd1": 1,
    "qWiQAc1nO9PkmRyano5RXG": 1,
    "iAkgxnyf8TDZlF2DFSVuTm": 1,
    "mzj9BFjDjQxfm2PlHMY3VA": 1,
    "nr8ok9lONWPW3cvbz15uMU": 1,
    "Y4WiQO79ijj3eYlo1AYWDL": 1,
    "7fBa6nvtkmBAt3zmaMKTze": 1,
    "H19bbpShOJik8uG2Ozsdn0": 1,
    "BfSLq8u6BvvqYjM24J68io": 1,
    "rUq6dstabrjyUg90coIRmb": 1,
    "ucDEz8KWHm4VjxSKho1KN4": 1,
    "b3VrVVlMXAOowW61AxA0DS": 1,
    "Js6qXPRh3NhWLjLX5BZmbZ": 1,
    "SjVvxDAbJPD45OXAHJ6MMT": 1,
    "Wk85mFOFutMwtjIdZXmAPu": 2,
    "USOk2N6cPpc8vp0h5SLNxf": 2,
    "U6RRkit593cTTQgpbccfWr": 2,
    "PjqBRAUEjjCYYiDQcczAh4": 1,
    "73d4pwjJPFrqKISjroZMvx": 1,
    "pfcNFGSIFoAyq67gnc1r6q": 1,
    "nSTRWhyU24cNVmShHy98Zt": 1,
    "0eXq3kGQTJHgh2L1wZzAk3": 1,
    "Pg4jEYxPYhToYJ1wnAptV0": 1,
    "YRCx3kNPYKmlkjGvlsJqbI": 1,
    "MQjXg2uZLFlAYjGLlO0jxn": 1,
    "Kka8uCYwpUQFaSGsBFDRuw": 1,
    "JHY0cQoen1Vsy94IJP4Jfr": 1,
    "eq2JcqcM0twsbAKcP3Um1S": 1,
    "VkNQGmLBs6TLzkmP2jIHNG": 1,
    "sHVbZTfQfNUzUaIpwVi7n2": 1,
    "Dth89xK78ETocf0cLtWyIC": 1,
    "x78jNQwidpwingIObw4Xaa": 1,
    "yzt2cdyQipzhievHr2VERm": 1,
    "U9ze44S2tqiaboh8Axjgtz": 1,
    "y3mxNVOIoggJrYVbW1yuH6": 1,
    "EUWBKzTGYOhZjpB6X0VEsa": 1,
    "M5hT4zmLWk714atBVfciM7": 1,
    "z6NDFIhhu1vh9uGy83pXZZ": 1,
    "lDiB6ToM8fWyk5wJRpuypw": 1,
    "lnZt052DBSkWj4sCibzoWu": 1,
    "UkglhwYW1lfdG96eStePoN": 1,
    "hBdJvjFbkGouimWraSueit": 1,
    "Hw1u302AtgMvZgX6SjcPsg": 1,
    "rGeptEEiSF3uyNI4lCmqWV": 1,
    "3VR7Yj789IetFoyjz6YO6L": 1,
    "ylFWFmtKvvcFF7plwHukwb": 1,
    "GHlpmcIA42RGTjKkkMLKzc": 1,
    "xRPsaXYgU9PGRpd76idOFB": 3,
    "NQUarAsYAs2YUKR6AiE8Zf": 3,
    "hgwFVDgCOc3IJeIggZheW3": 3,
    "HWKTR7o9kB66WY4gk4brDj": 2,
    "tou2Jqsk1YLOmRxo4ITcv5": 2,
    "bbxUv81UXt2KHfDqK7SHd3": 5,
    "WjtIC3DoKkvxYwxMyUHNwF": 8,
    "lAhP2QVt8AXYD3nZDXr70h": 6,
    "xJXGqIMW2VFVIr8ZPtkUlU": 1,
    "p38FHeP7oIHN92aAHZ1BLk": 1,
    "p4l9nLHRRWhPVdb4lYyF50": 1,
    "Baf6AYXGBxDU6aUVAfM7oU": 1,
    "WmGMAJiLciB6G3KmwW6QJg": 5
}


def parse_object_json_to_excel_row(object_json):
    row = {}

    for pset in pset_names:
        pset_data = object_json["property_sets"][f"{pset}"]
        for prop_name, prop_value in pset_data.items():
            val = prop_value["value"]

            if isinstance(val, list):
                val = "; ".join(val)

            row[f"{prop_name}"] = val

    return row


def parse_all_objects_to_df(objects_json):
    rows = [(parse_object_json_to_excel_row(object_json=o["data"]), o["data"]["object_id"]) for o in objects_json]

    rows_with_duplicates = []

    for row, object_id in rows:
        count = row_entry_counts.get(object_id, 1)
        for _ in range(count):
            rows_with_duplicates.append(row)

    return pd.DataFrame.from_records(rows_with_duplicates)


def get_object_library_data():
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }

    url = f"{API_ENDPOINT}/api/object/query"

    query_params = {
        "list_category": "wall-layer"
    }

    response = requests.get(url, headers=headers, params=query_params)

    data = response.json()

    return parse_all_objects_to_df(data)


if __name__ == "__main__":
    df = get_object_library_data()
    print(len(df))

    df.to_excel("test.xlsx")
