import Setting

setting = Setting.Config_Setting()
setting.Write_Setting()

cfg = setting.Read_Setting()
print(cfg)