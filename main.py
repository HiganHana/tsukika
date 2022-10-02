from higanhanaSdk.frame import DcMainframe

mf = DcMainframe.init("tsukika", init_mode=True)

if __name__ == '__main__':
    mf.setup_bot()
    mf.setup_flask()
    mf.setup_flask_sqlalchemy()
    mf.setup_flask_cold_trigger()