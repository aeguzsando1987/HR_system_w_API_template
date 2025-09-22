import secrets
import string

def generate_secret_key(length=32):
    """
    Genera SECRET_KEY segura para JWT.

    Args:
        length (int): Longitud de la clave (mínimo 32 caracteres recomendado)

    Returns:
        str: Clave secreta URL-safe
    """
    return secrets.token_urlsafe(length)

def generate_secure_password(length=16):
    """
    Genera contraseña segura con caracteres alfanuméricos y especiales.

    Args:
        length (int): Longitud de la contraseña

    Returns:
        str: Contraseña segura
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_database_password(length=20):
    """
    Genera contraseña para base de datos (sin caracteres especiales problemáticos).

    Args:
        length (int): Longitud de la contraseña

    Returns:
        str: Contraseña para BD
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == "__main__":
    print("=" * 60)
    print("GENERADOR DE CLAVES SEGURAS - BAPTA API TEMPLATE")
    print("=" * 60)

    print("\nPARA ACTUALIZAR .env EN PRODUCCION:")
    print("-" * 40)

    secret_key = generate_secret_key(32)
    db_password = generate_database_password(20)
    admin_password = generate_secure_password(12)

    print(f"SECRET_KEY={secret_key}")
    print(f"DATABASE_URL=postgresql://postgres:{db_password}@localhost:5432/pt_test")
    print(f"DEFAULT_ADMIN_PASSWORD={admin_password}")

    print("\nIMPORTANTE:")
    print("   1. Guarda estas claves en un lugar seguro")
    print("   2. Nunca compartas el SECRET_KEY")
    print("   3. Cambia la contraseña de PostgreSQL en tu servidor")
    print("   4. Actualiza .env con estos valores")
    print("   5. Reinicia la aplicación después del cambio")

    print("\nDESARROLLO:")
    print("   Para desarrollo, puedes mantener los valores actuales")
    print("   Usa estas claves solo en PRODUCCIÓN")

    print("\nPROXIMOS PASOS:")
    print("   1. Actualiza tu servidor PostgreSQL con la nueva contraseña")
    print("   2. Copia los valores a tu .env de producción")
    print("   3. Reinicia tu aplicación")

    print("\n" + "=" * 60)