from tsukika.bot import mf, base


if __name__ == "__main__":
    mf.setup_bot()
    mf.setup_flask()
    mf.setup_flask_sqlalchemy(_declarative_base=base)
    mf.setup_flask_cold_trigger(cold_trigger_token="Bw8usoXUJPAUuLvEtCdk")
    mf.run()
