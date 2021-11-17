def clean_mentioned_role(role: str) -> int:
    role = str(role)
    role = role.strip()
    try:
        return int(role.lstrip("<@&").rstrip(">"))
    except ValueError:
        return 0


def get_role_from_id(guild, role_id):
    for role in guild.roles:
        if role.id == role_id:
            return role
    return None
