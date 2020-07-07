import configparser


def config(key, default_value=None):
    c = configparser.ConfigParser()
    c.read("env.cfg")

    return c.get("ALL", key) or default_value
