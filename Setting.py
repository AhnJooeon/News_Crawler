import json

class Config_Setting():
    def __init__(self):
        print("Setting init")
    
    def Read_Setting(self):
        print("read")
        with open("config.json", "r", encoding="utf-8-sig") as f:
            config = json.load(f)
        return config

    def Write_Setting(self):
        new_config = {
            "keywords" : ["상 수상", "표창"],
            "client_id" : "UPJGOwLLHVof6piN_M8e",
            "client_secret" : "odN08XtmhN"
        }

        with open("config.json", "w", encoding="utf-8-sig") as f:
            json.dump(new_config, f, indent=4, ensure_ascii=False)
        


