# compat module for crypto functions
try:
    from Crypto.Cipher import AES
except ImportError:
    try:
        from Cryptodome.Cipher import AES
    except ImportError as imp_err:
        raise imp_err

__all__ = ['AES']
